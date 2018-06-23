import re
from rest_framework import serializers
from .models import User
from django_redis import get_redis_connection


class CreateUserSerializer(serializers.ModelSerializer):
    """
    注册序列化器
    """
    # 添加字段二次密码,短信验证码,同意协议
    password2 = serializers.CharField(min_length=8, max_length=20,write_only=True)
    sms_code = serializers.CharField(min_length=6, max_length=6,write_only=True)
    allow = serializers.BooleanField(default=False,write_only=True)

    # 用户名的唯一性校验---防止恶意请求
    def validate_username(self, value):
        if User.objects.filter(mobile=value).count() > 0:
            raise serializers.ValidationError('用户名已经被注册')
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
        try:
            if sms_code != conn.get('sms_%s' % mobile).decode():
                raise serializers.ValidationError('短信验证码不正确')
        except:
            raise serializers.ValidationError('短信验证码过期')
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
        return user

    class Meta:
        model = User
        # 需要字段
        fields = ('id','username', 'mobile', 'password', 'password2', 'sms_code', 'allow')
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