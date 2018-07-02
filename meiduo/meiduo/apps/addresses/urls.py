from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from . import views

urlpatterns = [
]

router = DefaultRouter()
router.register(prefix='address',viewset=views.AddressViewSet,base_name='address')
urlpatterns += router.urls