from rest_framework import serializers
from django_redis import get_redis_connection


from users.models import User


class SmsCodeSerializer(serializers.Serializer):
    image_code_id = serializers.UUIDField()
    image_code = serializers.CharField(min_length=4,max_length=4)

    def validate(self, attrs):
        # 1. 校验图片验证码
        image_code_id = attrs['image_code_id']
        image_code = attrs['image_code']
        conn = get_redis_connection('verify_codes')
        code = conn.get('img_%s'%image_code_id)
        mobile = self.context.get('mobile')
        if not code:
            raise ValueError('验证码过失效')
        # 对比图片验证码之前,先删除验证码
        if image_code.upper() != code.decode().upper():
            raise ValueError('验证码错误')
        # 2. 校验手机号
        # 2.1 是否已经被注册过
        if mobile in [user.mobile for user in User.objects.all()]:
            raise ValueError('该手机号已经被注册过')
        # 2.2 60秒内是否已经发送过短信
        if conn.get('is_sms_%s'%mobile):
            raise ValueError('请不要过于频繁点击发送验证码')
        return attrs




