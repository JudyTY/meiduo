from django.db import models
from meiduo.utils.models import BaseModel
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer
from django.conf import settings

from . import constans


# Create your models here.

class oAuthQQUser(BaseModel):
    # 腾讯服务器生成的qq用户对外的唯一标识，添加索引
    openid = models.CharField(max_length=64, db_index=True, verbose_name='openid')
    # 添加外键--对应用户模型类
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')

    class Meta:
        db_table = 'tb_oauth_qq'
        verbose_name = 'QQ登录用户数据'
        verbose_name_plural = verbose_name

    @staticmethod
    def get_access_token(openid):
        """
        生成获取短信验证码需要的令牌
        :return: token
        """
        serial = TJWSSerializer(settings.SECRET_KEY,expires_in=constans.DANGEROURS_TOKEN_EXPIRES)
        # dumps方法生成的token是bytes类型
        access_token = serial.dumps({'openid': openid}).decode()
        return access_token

    @staticmethod
    def decode_access_token(access_token):
        """
        从access_token中获取openid
        :param access_token:
        :return:
        """
        serial = TJWSSerializer(settings.SECRET_KEY,expires_in=constans.DANGEROURS_TOKEN_EXPIRES)
        try:
            openid = str(serial.loads(access_token).get('openid'))
        except:
            return None
        return openid



