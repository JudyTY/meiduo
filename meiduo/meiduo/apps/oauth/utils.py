from urllib.parse import urlencode
from django.conf import settings


class OAuthQQ(object):
    # 处理qq登录工具类
    def __init__(self,  app_id=None, redirect_uri=None, app_key=None, state=None):
        # QQ互联注册的app_id
        self.app_id = app_id or settings.QQ_APP_ID
        # QQ互联注册的app_key
        self.app_key = app_key or settings.QQ_APP_KEY
        # QQ登录完成后的回调地址
        self.redirect_uri = redirect_uri or settings.QQ_REDIRECT_URL
        # 本地登录前的地址记录
        self.state = state or '/'

    def get_oauthqq_url(self):
        """
        生成登录qq的地址
        :return: 用于用户登录qq的地址
        """
        # 获取authentication_code的地址
        url = 'https://graph.qq.com/oauth2.0/authorize'

        # 从qq文档中获取的请求参数
        query_dict = {
            'response_type': 'code',
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'state': 'code',
            'scope': 'get_user_info',
        }
        query_url = url + '?' + urlencode(query_dict)
        return query_url

    def get_access_token_url(self,code):
        """
        生成获取access_token的地址
        :param code:
        :return:
        """
        url = 'https://graph.qq.com/oauth2.0/token'
        query_dict = {
            'grant_type': 'authorization_code',
            'client_id': self.app_id,
            'client_secret': self.app_key,
            'code': code,
            'redirect_uri': self.redirect_uri,
        }
        get_token_url = url + '?' + urlencode(query_dict)
        return get_token_url

    def get_open_id(self,access_token):
        """
        生成获取openid的地址
        :param access_token:
        :return:
        """
        url = 'https://graph.qq.com/oauth2.0/me'
        query_dict = {
            'access_token': access_token,
        }
        get_openid_url = url + '?' + urlencode(query_dict)
        return get_openid_url

