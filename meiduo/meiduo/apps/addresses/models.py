from django.db import models
from rest_framework import serializers

from areas.models import Areas
# Create your models here.
from meiduo.utils.models import BaseModel


class Addresses(BaseModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    address = models.CharField(max_length=50, verbose_name='详细收货地址',default='')
    # 省市区关联字段
    province = models.ForeignKey('areas.Areas', verbose_name='省级行政区', on_delete=models.PROTECT,
                                 related_name='province_address')
    city = models.ForeignKey('areas.Areas', verbose_name='市级行政区', on_delete=models.PROTECT, related_name='city_address')
    district = models.ForeignKey('areas.Areas', verbose_name='县级行政区', on_delete=models.PROTECT,
                                 related_name='district_address')
    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    phone = models.CharField(max_length=11, verbose_name='手机号码')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_addresses'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        ordering = ['-update_date']
