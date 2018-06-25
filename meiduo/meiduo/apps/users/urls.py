from django.conf.urls import url
from users import views
# restframeworkjWT提供了登录验证的功能,obtain_jwt_token==于类.asview()
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    # 用户名的唯一校验
    url(r'usernames/(?P<username>.{5,20})/$',views.UserName.as_view()),
    # 手机号码的唯一校验
    url(r'usermobiles/(?P<mobile>1[3-8]\d{9})/$', views.UserMobile.as_view()),
    # 登录路由
    url(r'authorizations/$', obtain_jwt_token,name='authorizations'),
    # 注册路由
    url(r'$', views.UserRigister.as_view()),

]
