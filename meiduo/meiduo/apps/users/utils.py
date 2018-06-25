import re

from django.contrib.auth.backends import ModelBackend

from .models import User


def jwt_response_payload_handler(token,user=None,request=None):
    """
    自定义响应的数据
    :param token:token数据
    :param request:
    :param user:
    :return:
    """
    return {
        'token':token,
        'id':user.id,
        'username':user.username,
        'mobile':user.mobile
    }


def get_user_acount(acount):
    # 添加手机号的验证方法
    if re.match(r'^1[345789]\d{9}$',acount):
        user = User.objects.get(mobile=acount)
    # 添加邮箱的验证方法
    elif re.match(r'.+@.+',acount):
        user = User.objects.get(email=acount)
    else:
        try:
            user = User.objects.get(username=acount)
        except :
            return None
    return user



class UsernameMobileAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_acount(username)
        if user and user.check_password(password):
            return user