from django_redis import get_redis_connection
from rest_framework import serializers
from oauth.models import oAuthQQUser

from users.models import User

class OAuthQQUserSerializer(serializers.Serializer):
    access_token = serializers.CharField(label='携带openid的token')
    mobile = serializers.CharField(label='手机号')
    sms_code = serializers.CharField(label='短信验证码',min_length=6,max_length=6)
    password = serializers.CharField(label='短信验证码',min_length=6,max_length=20)

    def validate(self, attrs):
        access_token = attrs.get('access_token')
        openid = oAuthQQUser.decode_access_token(access_token)
        if not openid:
            return serializers.ValidationError('access_token不正确')
        attrs['openid'] = openid
        mobile = attrs.get('mobile')
        sms_code = attrs.get('sms_code')
        conn = get_redis_connection('verify_codes')
        if not conn.get('sms_%s' % mobile):
            raise serializers.ValidationError('短信验证码过期或手机号输入错误')
        if sms_code != conn.get('sms_%s' % mobile).decode():
            raise serializers.ValidationError('短信验证码不正确')
        password = attrs.get('password')
        try:
            user = User.objects.get(mobile=mobile)
            attrs['user'] = user
            if not user.check_password(password):
                raise serializers.ValidationError('密码输入错误')
        except:
            pass
        return attrs

    def create(self, validated_data):
        user = validated_data.get('user')
        if not user:
            user = User.objects.create_user(
                username='meiduo_'+str(validated_data['mobile']),
                mobile=validated_data['mobile'],
                password=validated_data['password'],
            )
        oAuthQQUser.objects.create(openid=validated_data['openid'],
                                       user=user)
        return user
