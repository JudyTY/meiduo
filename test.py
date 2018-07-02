# a = {'a':123,
#      "b":5656}
#
# del a['a','b']

# print(a)
# 为celery使用django配置文件进行设置
import os,django
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo.settings.dev'
django.setup()
from meiduo.apps.addresses.serializers import AddressAddSerializer

add = AddressAddSerializer()
print(add)