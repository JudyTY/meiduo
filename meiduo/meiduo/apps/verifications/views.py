import random

from django.http import HttpResponse
from django.shortcuts import render
from django.db import models
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django_redis import get_redis_connection

from meiduo.apps.verifications.serializers import SmsCodeSerializer
from . import constants,serializers
# Create your views here.
from meiduo.libs.captcha.captcha import captcha
from meiduo.libs.yuntongxun.sms import CCP

class ImageCode(APIView):
    """
    图片验证码
    """
    def get(self,request,image_code_id):
        # 1. 调用接口,生成图片,记录验证码
        text,image = captcha.generate_captcha()
        # 2. 记录键image_code_id,值验证码
        conn = get_redis_connection('verify_codes')
        conn.setex("img_%s"%image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES,text)
        # 3. 返回响应
        return HttpResponse(image,content_type='images/jpg')


class SmsCode(GenericAPIView):
    """
    短信验证码
    """
    serializer_class = serializers.SmsCodeSerializer
    def get(self,request,mobile):
        serial = SmsCodeSerializer(data=request.query_params,context={'mobile': mobile})
        # 1. 使用序列化器校验
        try:
            serial.is_valid(raise_exception=True)
        except ValueError as e:
            return Response('%s'%e,status=401)
        # 2. 发送短信验证码
        num = random.randint(0,999999)
        # 2.1 存储短信验证码数据
        # 创建管道减少与redis数据库交互
        conn = get_redis_connection('verify_codes')
        pl = conn.pipeline()
        pl.multi()
        pl.setex('is_sms_%s'%mobile,constants.SMS_ISSEND_REDIS_EXPIRES,1)
        pl.setex('sms_%s'%mobile,constants.SMS_CODE_REDIS_EXPIRES,num)
        pl.execute()
        # 2.2 调用接口发送数据
        # ccp = CCP()
        # ccp.send_template_sms(mobile,"%06d"%num,1)
        return HttpResponse('ok',status=200)


