from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, GenericAPIView, UpdateAPIView, RetrieveAPIView
from django.views import View
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.core.mail import send_mail

from django.conf import settings
from verifications.serializers import ImageCodeSerializer, SmsCodeTokenSerializer

# Create your views here.
from users.models import User
from .serializers import *
from .utils import get_user_acount


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


# 忘记密码
# 第一步
class ImagecodeCheckView(GenericAPIView):
    serializer_class = ImageCodeSerializer

    def get(self, request, acount):
        serial = self.get_serializer(data=request.query_params)
        try:
            serial.is_valid(raise_exception=True)
        except ValueError as e:
            return Response({'image_code_error': '%s' % e}, status=400)

        user = get_user_acount(acount)  # type:User
        # 验证用户是否存在
        if not user:
            return Response({'username_error': '用户不存在'}, status=400)

        token = user.generate_sms_token()
        # mobile是隐私信息,需要进一步处理
        mobile = re.sub(r'(\d{3})\d{4}(\d{4})', r'\1****\2', user.mobile)
        return Response({'mobile': mobile, 'token': token})


# 第二步--verifitions--views
class SmscodeCheckView(GenericAPIView):
    serializer_class = SmsCodeTokenSerializer

    def get(self, request, account):
        serial = self.get_serializer(data=request.query_params)
        try:
            serial.is_valid(raise_exception=True)
        except ValueError as e:
            return Response({'sms_code_error': '%s' % e}, status=400)

        user = serial.user  # type:User
        # 验证用户是否存在
        if not user:
            return Response({'mobile_error': '用户不存在'}, status=400)
        token = user.generate_pwd_token()
        # 重置密码时需要前端传来的id与token中的id进行比对
        return Response({'token': token, 'id': user.id})


class PasswordView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ResetPasswordSerializer

    def post(self, request, pk):
        return self.update(request, pk)


class UserDetailView(RetrieveAPIView):
    # 返回用户的详细信息
    serializer_class = UserDetailSerializer
    # 设置登录才能访问此视图类
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # 当视图类进行dispatch分发时==>会将request对象保存为视图类的request属性==>request对象拥有user属性即登录的用户
        return self.request.user


# 以下使用post方法请求
# class EmailView(CreateAPIView):
#     """提交用户的邮箱"""
#     # 设置登录权限
#     permission_classes = [IsAuthenticated]
#
#     # 重写get_serializer方法--使用自己定义的序列化器
#     def get_serializer(self, *args, **kwargs):
#         # 使用更新邮箱的序列化器,参数:1. 模型类对象为当前登录用户,数据为当前请求对象的参数
#         return EmailSerializer(instance=self.request.user, data=self.request.data)

# 以下使用put方法请求
class EmailView(UpdateAPIView):
    """提交用户的邮箱"""
    # 设置登录权限
    permission_classes = [IsAuthenticated]
    # 需要指定序列化器
    serializer_class = EmailSerializer

    # 重写get_object方法--指定需要修改的对象
    def get_object(self):
        return self.request.user

        # 以下发送邮件的方法只能放在序列化器中,需要保证对象的邮箱信息被更新==>放入update方法中
        # def put(self, request):
        #     email = request.data.get('email')
        #     token = ''
        #     url = 'www.baidu.com'
        #     header = '美多邮箱激活'
        #     message = url + token
        #     send_mail(subject=header, message=message, from_email=settings.EMAIL_FROM, recipient_list=[email])
        #     return Response({'message': 'ok!'})


"""
以下为激活邮箱的链接:
http://www.meiduo.site:8080/success_verify_email.html?token=eyJleHAiOjE1MzAyNzMyOTQsImFsZyI6IkhTMjU2IiwiaWF0IjoxNTMwMjcyNjk0fQ.eyJlbWFpbCI6IjE3NTU5NzQ1NDBAcXEuY29tIiwiaWQiOjEwfQ.g62akteoB1zBxaFOGsRLccEDxxBFFHFaMFnuN8StlbI
"""


class VerifyEmailView(APIView):
    """用户email的激活状态"""

    def get(self, request):
        # 拿到查询字符串中的token值
        token = request.query_params.get('token')
        if not token:
            return Response(status=400)
        # 使用模型类中的方法解析token,返回的值是None/user对象
        user = User.decode_email_token(token=token)
        if not user:
            return Response(status=400)
        # 将user的email激活状态改为True
        user.email_active = True
        user.save()
        return Response({"message": 'ok!'})
