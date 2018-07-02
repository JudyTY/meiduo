from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.mixins import CacheResponseMixin


from .models import Areas
from .serializers import AreasListSerializer, AreasRetrieverSerializer


# Create your views here.

class AreasViewSet(CacheResponseMixin,ReadOnlyModelViewSet):
    # 不以分页显示
    pagination_class = None
    """list==>省级行政区的列表页,retrieve==>指定父级id的详情页"""
    def get_serializer_class(self):
        """
        重写get_serializer_class分别返回列表视图和详情视图所使用的不同的序列化器
        :return:
        """
        if self.action == "list":
            return AreasListSerializer
        else:
            return AreasRetrieverSerializer

    def get_queryset(self):
        """
        重写get_queryset方法,当获取列表页时,只查询省级行政区,即没有父级id的数据
        :return:
        """
        if self.action == "list":
            return Areas.objects.filter(parent_id=None)
        else:
            return Areas.objects.all()
