from rest_framework import serializers
from django_redis import get_redis_connection
from users.models import User
from users.utils import get_user_acount


# from ...apps.users.models import User


class SmsCodeSerializer(serializers.Serializer):
    image_code_id = serializers.UUIDField()
    image_code = serializers.CharField(min_length=4,max_length=4)

    def validate(self, attrs):
        # 1. 校验图片验证码
        image_code_id = attrs['image_code_id']
        image_code = attrs['image_code']
        conn = get_redis_connection('verify_codes')
        code = conn.get('img_%s'%image_code_id)
        mobile = self.context['view'].kwargs['mobile']
        if not code:
            raise ValueError('图片验证码失效')
        # 对比图片验证码之前,先删除验证码
        if image_code.upper() != code.decode().upper():
            raise ValueError('图片验证码错误')
        # 2. 校验手机号
        # 2.1 是否已经被注册过
        # if User.objects.filter(mobile=mobile).count():
        #     raise ValueError('该手机号已经被注册过')
        # 2.2 60秒内是否已经发送过短信
        if conn.get('is_sms_%s'%mobile):
            raise ValueError('请不要过于频繁点击发送验证码')
        return attrs


class ImageCodeSerializer(serializers.Serializer):
    """
    用于忘记密码第一步的图片验证码的验证操作
    """
    image_code_id = serializers.UUIDField()
    image_code = serializers.CharField(min_length=4,max_length=4)

    def validate(self, attrs):
        # 1. 校验图片验证码
        image_code_id = attrs['image_code_id']
        image_code = attrs['image_code']
        conn = get_redis_connection('verify_codes')
        code = conn.get('img_%s'%image_code_id)
        if not code:
            raise ValueError('图片验证码失效')
        # 对比图片验证码之前,先删除验证码
        if image_code.upper() != code.decode().upper():
            raise ValueError('图片验证码错误')
        return attrs


class SmsCodeTokenSerializer(serializers.Serializer):
    sms_code = serializers.CharField(min_length=6, max_length=6)
    def validate(self, attrs):
        # 短信验证码的校验
        sms_code = attrs.get('sms_code', '1')
        acount = self.context['view'].kwargs['account']
        self.user = get_user_acount(acount) # type:User
        mobile = self.user.mobile
        conn = get_redis_connection('verify_codes')
        if not conn.get('sms_%s' % mobile):
            raise ValueError('短信验证码过期或手机号输入错误')
        if sms_code != conn.get('sms_%s' % mobile).decode():
            raise ValueError('短信验证码不正确')
        return attrs