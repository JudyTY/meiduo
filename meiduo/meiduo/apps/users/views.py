from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from django.views import View


# Create your views here.
from users.models import User
from .serializers import *



# 验证用户名的唯一性
class UserName(View):
    def get(self, request, username):
        if User.objects.filter(username=username).count() > 0:
            return JsonResponse(data={'username_error': '该用户名已经被注册过'})
        return JsonResponse(data={'success_info': ''})


# 验证手机号码的唯一性
class UserMobile(View):
    def get(self, request, mobile):
        if User.objects.filter(mobile=mobile).count() > 0:
            return JsonResponse(data={'mobile_error': '该手机号已经被注册过'})
        return JsonResponse(data={'success_info': ''})

# 注册请求发起
class UserRigister(CreateAPIView):
    serializer_class = CreateUserSerializer
