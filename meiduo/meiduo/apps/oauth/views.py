
import re
from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from urllib.request import urlopen
from urllib.parse import parse_qs

# Create your views here.
from rest_framework_jwt.settings import api_settings

from .utils import OAuthQQ
from oauth.models import oAuthQQUser
from . import serializers


class QQAuthURLView(APIView):
    """
    第三方QQ登录
    """
    def get(self,request):
        """
        :param request:
        :return: QQ登录地址
        """
        # 登录请求时的地址
        state = request.query_params.get('state')
        # 使用工具类
        oauth_qq = OAuthQQ(state=state)
        url = oauth_qq.get_oauthqq_url()
        return Response({'url':url})

class QQAuthUserView(GenericAPIView):
    serializer_class = serializers.OAuthQQUserSerializer
    def get(self,request):
        code = request.query_params.get('code')
        # 使用工具类
        oauth_qq = OAuthQQ()
        url = oauth_qq.get_access_token_url(code)
        try:
            response = urlopen(url).read().decode()
            access_token = parse_qs(response).get('access_token')[0]
        except:
            return Response(status=404)
        try:
            url = oauth_qq.get_open_id(access_token)
            response = urlopen(url).read().decode()[11:-5:]
            openid = re.match(r'.+"openid":"(.+)"',response).group(1)
        except:
            return Response(status=404)
        try:
            qquser = oAuthQQUser.objects.get(openid=openid)
        except:
            access_token = oAuthQQUser.get_access_token(openid)
            return Response({'access_token':access_token})
        user = qquser.user
        jwt_playload = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode = api_settings.JWT_ENCODE_HANDLER
        playload = jwt_playload(user)
        token = jwt_encode(playload)
        return Response({
            'token':token,
            'user_id':user.id,
            'username':user.username
                         })

    def post(self,request):
        serial = self.get_serializer(data=request.data)
        try:
            serial.is_valid(raise_exception=True)
        except Exception as e:
            return Response({'message','%s'%e},status=400)
        user = serial.save()
        jwt_playload = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode = api_settings.JWT_ENCODE_HANDLER
        playload = jwt_playload(user)
        token = jwt_encode(playload)
        return Response({
            'token':token,
            'user_id':user.id,
            'username':user.username
                         })


