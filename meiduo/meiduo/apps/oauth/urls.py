from django.conf.urls import url
from . import views

urlpatterns = [
    # qq第三方登录
    url(r'qq/authorization/$', views.QQAuthURLView.as_view()),
    url(r'qq/user/$', views.QQAuthUserView.as_view()),
]
