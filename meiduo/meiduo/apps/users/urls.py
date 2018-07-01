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
    # 忘记密码的第一步图片验证操作
    url(r'image_code/(?P<acount>\w{6,20})/$', views.ImagecodeCheckView.as_view()),
    # 忘记密码的第二步提交短信验证码操作
    url(r'accounts/(?P<account>\w{5,20})/password/token/$', views.SmscodeCheckView.as_view()),
    # 忘记密码的第三步/重置密码
    url(r'(?P<pk>\d+)/password/$', views.PasswordView.as_view()),
    # 显示个人信息
    url(r'user/$', views.UserDetailView.as_view()),
    # 邮箱填写及激活邮件的发送
    url(r'emails/$', views.EmailView.as_view()),
    # 激活邮箱
    url(r'emails/verification/$', views.VerifyEmailView.as_view()),
    # 注册路由
    url(r'$', views.UserRigister.as_view()),
]