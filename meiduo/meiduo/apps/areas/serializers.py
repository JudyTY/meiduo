from rest_framework import serializers

from areas.models import Areas


class AreasListSerializer(serializers.ModelSerializer):
    """返回省级行政区列表页"""
    class Meta:
        model = Areas
        fields = ('id', 'name')


class AreasRetrieverSerializer(serializers.ModelSerializer):
    """指定父级的详情信息,包含下级行政区列表"""
    # 为了areas表可能作为多个表的外键使用,需要使用不同的名字,以免引发互斥锁
    subs = AreasListSerializer(many=True, read_only=True)
    class Meta:
        model = Areas
        fields = ('id', 'name', 'subs')
