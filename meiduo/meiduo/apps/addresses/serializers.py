import re
from rest_framework import serializers

from addresses.models import Addresses
from areas.models import Areas
from users.models import User


class AddressListSerializer(serializers.ModelSerializer):
    province = serializers.StringRelatedField(label='省级行政区')
    city = serializers.StringRelatedField(label='省级行政区')
    district = serializers.StringRelatedField(label='省级行政区')

    class Meta:
        model = Addresses
        fields = ('id', 'title', 'address', 'province', 'city', 'district','province_id', 'city_id', 'district_id', 'receiver', 'phone', 'tel', 'email')


class AddressAddSerializer(serializers.ModelSerializer):
    province_id = serializers.CharField()
    city_id=serializers.CharField()
    district_id = serializers.CharField()
    user_id = serializers.CharField()
    class Meta:
        model = Addresses
        fields = (
                  'title', 'address', 'province_id', 'city_id', 'district_id', 'receiver', 'phone', 'tel', 'email', 'user_id')
        extra_kwargs = {
            'tel': {'required': False,'allow_null': True},
            'email': {'required': False,'allow_null': True},
            'title': {'required': False, 'allow_null': True},
        }

    def validate(self, attrs):
        if not re.match(r'^1[345789]\d{9}$', attrs['phone']):
            raise serializers.ValidationError('手机号格式错误')
        if attrs['email'] and not re.match(r'^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$', attrs['email']):
            raise serializers.ValidationError('邮箱格式不正确')
        try:
            province = Areas.objects.get(id=attrs['province_id'])
            city = Areas.objects.get(id=attrs['city_id'])
            district = Areas.objects.get(id=attrs['district_id'])
        except:
            raise serializers.ValidationError('行政区域填写不正确')
        if str(district.parent_id) != str(attrs['city_id']) or str(city.parent_id) != str(attrs['province_id']):
            raise serializers.ValidationError('行政区域填写不正确')
        try:
            attrs['user'] = User.objects.get(id=attrs['user_id'])
        except:
            raise serializers.ValidationError('没有该用户')
        attrs['province']=province
        attrs['city']=city
        attrs['district']=district
        attrs['title'] = str(attrs['receiver'])+str(attrs['city'])
        return super().validate(attrs)

