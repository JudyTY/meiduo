import re

from django.contrib.auth.backends import ModelBackend

from .models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义响应的数据
    :param token:token数据
    :param request:
    :param user:
    :return:
    """
    return {
        'token': token,
        'id': user.id,
        'username': user.username,
        'mobile': user.mobile
    }


# 自定义一个函数,用来获取不同的字段名登录的模型类对象
def get_user_acount(acount):
    # 添加手机号的验证方法
    if re.match(r'^1[345789]\d{9}$', acount):
        try:
            user = User.objects.get(mobile=acount)
        except:
            return None
    # 添加邮箱的验证方法
    elif re.match(r'.+@.+', acount):
        try:
            user = User.objects.get(email=acount)
        except:
            return None
    else:
        try:
            user = User.objects.get(username=acount)
        except:
            return None
    return user


# 定义登录功能使用的视图类
class UsernameMobileAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_acount(username)
        if user and user.check_password(password):
            return user
