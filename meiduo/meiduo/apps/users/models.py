from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer
# Create your models here.

from meiduo.settings.dev import SECRET_KEY
from users import constans


# django框架提供了User用户类
class User(AbstractUser):
    """
    用户模型类
    """
    # 新增默认地址外键字段
    default_address = models.ForeignKey('addresses.Addresses',
                                        related_name='users', null=True, blank=True, on_delete=models.SET_NULL,
                                        verbose_name='默认地址')
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    # 新增邮箱激活状态
    email_active = models.BooleanField(default=False, verbose_name='邮箱激活状态')

    class Meta:
        # 表名
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def generate_sms_token(self):
        """
        生成获取短信验证码需要的令牌
        :return: token
        """
        serial = TJWSSerializer(SECRET_KEY, expires_in=constans.DANGEROURS_TOKEN_EXPIRES)
        # dumps方法生成的token是bytes类型
        self.token = serial.dumps({'mobile': self.mobile}).decode()
        return self.token

    @staticmethod
    def decode_sms_token(token):
        serial = TJWSSerializer(SECRET_KEY, expires_in=constans.DANGEROURS_TOKEN_EXPIRES)
        try:
            mobile = serial.loads(token).get('mobile')
        except:
            return None
        return mobile

    def generate_pwd_token(self):
        """
        生成获取短信验证码需要的令牌
        :return: token
        """
        serial = TJWSSerializer(SECRET_KEY, expires_in=constans.DANGEROURS_TOKEN_EXPIRES)
        # dumps方法生成的token是bytes类型
        self.token = serial.dumps({'id': self.id}).decode()
        return self.token

    @staticmethod
    def decode_pwd_token(token, id):
        serial = TJWSSerializer(SECRET_KEY, expires_in=constans.DANGEROURS_TOKEN_EXPIRES)
        try:
            user_id = str(serial.loads(token).get('id'))
            if id != user_id:
                return False
        except:
            return False
        return True

    def generate_email_message(self):
        """用于生成激活邮箱的链接"""
        serial = TJWSSerializer(SECRET_KEY, expires_in=constans.DANGEROURS_TOKEN_EXPIRES)
        # token中储存用户id和用户email
        token = serial.dumps({'id': self.id, 'email': self.email}).decode()
        message = 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token
        return message

    @staticmethod
    def decode_email_token(token):
        """
        解析邮件激活操作返回的token
        :param token:
        :return: user/None
        """
        serial = TJWSSerializer(SECRET_KEY, expires_in=constans.DANGEROURS_TOKEN_EXPIRES)
        try:
            # 如果在此token取不到id和email,证明是伪造请求
            user_id = str(serial.loads(token).get('id'))
            email = str(serial.loads(token).get('email'))
        except:
            return None
        try:
            # 以id和email两个条件获取user对象,获取不到则说明用户的邮箱对应不上==>服务器生成激活链接出错/伪造请求
            user = User.objects.get(id=user_id, email=email)
        except:
            return None
        return user
