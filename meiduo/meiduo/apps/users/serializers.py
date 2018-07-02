import re
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from django.core.mail import send_mail

from django.conf import settings
from .models import User
from django_redis import get_redis_connection
from celery_tasks.email.tasks import celery_send_email


class CreateUserSerializer(serializers.ModelSerializer):
    """
    注册序列化器
    """
    # 添加字段二次密码,短信验证码,同意协议
    password2 = serializers.CharField(min_length=8, max_length=20, write_only=True)
    sms_code = serializers.CharField(min_length=6, max_length=6, write_only=True)
    allow = serializers.BooleanField(default=False, write_only=True)
    # 新增jwt的token字段,用于返回给浏览器
    token = serializers.CharField(read_only=True, required=False)

    # 用户名的唯一性校验---防止恶意请求
    def validate_username(self, value):
        if User.objects.filter(mobile=value).count() > 0:
            raise serializers.ValidationError('用户名已经被注册')
        if re.match(r'^\d.+', value):
            raise serializers.ValidationError('用户名不能以数字开头')
        return value

    # 手机号的唯一性校验---防止恶意请求;手机号的格式校验
    def validate_mobile(self, value):
        if User.objects.filter(mobile=value).count() > 0:
            raise serializers.ValidationError('手机号已经被注册')
        if not re.match(r'^1[345789]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    # 协议的勾选校验
    def validate_allow(self, value):
        if not value:
            raise serializers.ValidationError('请勾选同意')
        return value

    def validate(self, data):
        # 密码校验
        # 格式校验
        if not re.match(r'.{8,20}', data['password']):
            raise serializers.ValidationError('请输入8~20位的密码')
        # 比对校验
        if data['password2'] != data['password']:
            raise serializers.ValidationError('两次密码输入不一致')
        # 短信验证码的校验
        sms_code = data.get('sms_code', '1')
        mobile = data.get('mobile')
        conn = get_redis_connection('verify_codes')
        if not conn.get('sms_%s' % mobile):
            raise serializers.ValidationError('短信验证码过期或手机号输入错误')
        if sms_code != conn.get('sms_%s' % mobile).decode():
            raise serializers.ValidationError('短信验证码不正确')
        return data

    def create(self, validated_data):
        """
        新建用户
        :param validated_data:
        :return:
        """
        # 删除多余字段
        del validated_data['password2'], validated_data['sms_code'], validated_data['allow']
        # 继承父类create方法
        user = super().create(validated_data)
        # 使用AbstractUser提供的加密方式
        user.set_password(validated_data['password'])
        user.save()

        # 注册完成后,返回jwt的token给浏览器

        # 得到生成playload载荷方法
        jwt_playload = api_settings.JWT_PAYLOAD_HANDLER
        # 得到生成token方法
        jwt_encode = api_settings.JWT_ENCODE_HANDLER
        # palyload中储存user对象的属性
        playload = jwt_playload(user)
        # 生成token,将token添加到user的属性中
        token = jwt_encode(playload)
        user.token = token
        # 此时返回的user一并返回了token
        return user

    class Meta:
        model = User
        # 需要字段
        fields = ('id', 'username', 'mobile', 'password', 'password2', 'sms_code', 'allow', 'token')
        # 其它说明
        extra_kwargs = {
            'id': {'read_only': True},
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }


class ResetPasswordSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'password', 'password2', 'token')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        token = attrs.get('token')
        id = self.context['view'].kwargs['pk']
        allow = User.decode_pwd_token(token=token, id=id)
        if not allow:
            return serializers.ValidationError('无效token')

        if password2 != password:
            return serializers.ValidationError('两次输入密码不一致')
        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class UserDetailSerializer(serializers.ModelSerializer):
    # 返回用户个人中心信息序列化器
    class Meta:
        model = User
        # 设置返回的字段
        fields = ('id', 'username', 'mobile', 'email', 'email_active')


class EmailSerializer(serializers.ModelSerializer):
    """保存用户的邮箱信息"""

    class Meta:
        model = User
        # 指定字段用于返回
        fields = ('id', 'email')
        # email为必填项
        extra_kwargs = {'email': {
            'required': True,
        }}

    def validate_email(self, value):
        if not re.match(r'^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$', value):
            raise serializers.ValidationError('邮箱格式不正确')
        try:
            User.objects.get(email=value)
            raise serializers.ValidationError('此邮箱已经被注册过')
        except:
            return value

    def update(self, instance, validated_data):
        # 保存用户邮箱
        instance.email = validated_data['email']
        instance.save()
        # 激活邮件的发送
        email = validated_data['email']
        # token中需记录用户id与用户邮箱,将message的生成放到模型类的方法中
        # token = ''
        # url = 'www.baidu.com'
        # header = '美多邮箱激活'
        message = instance.generate_email_message()
        # 发送邮件是耗时操作,放入celery中
        celery_send_email(email=email, message=message)
        return instance
