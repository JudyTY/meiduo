from django.conf.urls import url
from rest_framework.routers import DefaultRouter


from areas.views import AreasViewSet

urlpatterns = [
]


# 生成区域的路由,list及retrieve
router = DefaultRouter()
router.register(prefix='areas',viewset=AreasViewSet,base_name='areas')
urlpatterns += router.urls