from django.conf.urls import url
from users import views

urlpatterns = [
    # 用户名的唯一校验
    url(r'usernames/(?P<username>.{5,20})/$',views.UserName.as_view()),
    # 手机号码的唯一校验
    url(r'usermobiles/(?P<mobile>1[3-8]\d{9})/$', views.UserMobile.as_view()),
    # 注册路由
    url(r'$', views.UserRigister.as_view()),

]
