from django.conf.urls import url
from meiduo.apps.verifications import views

urlpatterns = [
    # 图片验证码
    url(r'image_codes/(?P<image_code_id>.+)/$',views.ImageCode.as_view()),
    # 短信验证码
    url(r'sms_codes/(?P<mobile>1[3-8]\d{9})/$',views.SmsCode.as_view()),
]
