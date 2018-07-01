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
from celery_tasks.sms.tasks import send_sms_code
from users.models import User


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
        # 使用get_serializer方法给序列化器对象补充view属性,可以拿到词self的属性
        serial = self.get_serializer(data=request.query_params)
        # 1. 使用序列化器校验
        try:
            serial.is_valid(raise_exception=True)
        except ValueError as e:
            return Response(data={'image_code_error':'%s'%e} if '图片' in ("%s"%e) else {'sms_code_error':'%s'%e},status=401,content_type='application/json')
        # 2. 发送短信验证码
        num = '%06d'%random.randint(0,999999)
        # 2.1 存储短信验证码数据
        # 创建管道减少与redis数据库交互
        conn = get_redis_connection('verify_codes')
        pl = conn.pipeline()
        pl.multi()
        pl.setex('is_sms_%s'%mobile,constants.SEND_SMS_CODE_INTERVAL,1)
        pl.setex('sms_%s'%mobile,constants.SMS_CODE_REDIS_EXPIRES,num)
        pl.execute()
        print(num)
        # 2.2 调用接口发送数据
        # ccp = CCP()
        # time = str(constants.SMS_CODE_REDIS_EXPIRES / 60)
        # ccp.send_template_sms(mobile, ["%06d"%num,time], constants.SMS_TEMP_ID)
        # print(num)
        send_sms_code.delay(mobile,num)
        return HttpResponse('ok',status=200)


class SmsCodeTokenView(APIView):
    """
    用于忘记密码的第二步验证token和2.1发送短信
    """
    def get(self,request):
        token = request.query_params.get('token')
        mobile = User.decode_sms_token(token)
        user = User.objects.get(mobile=mobile)
        num = '%06d'%random.randint(0,999999)
        conn = get_redis_connection('verify_codes')
        if not user:
            return Response({'mobile_eroor':'手机号还没有注册过'},status=400)
        if conn.get('is_sms_%s'%mobile):
            return Response({'sms_code_error':'请不要过于频繁点击发送验证码'},status=400)
        pl = conn.pipeline()
        pl.multi()
        pl.setex('is_sms_%s'%mobile,constants.SEND_SMS_CODE_INTERVAL,1)
        pl.setex('sms_%s'%mobile,constants.SMS_CODE_REDIS_EXPIRES,num)
        pl.execute()
        print(num)
        send_sms_code.delay(mobile,num)
        return Response({'message:ok!'},status=200)






