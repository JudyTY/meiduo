from celery import Celery

# 创建celery实例
app = Celery('meiduo')

# 为celery使用django配置文件进行设置
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'

# 配置
app.config_from_object('celery_tasks.config')

# 自动检索任务
app.autodiscover_tasks(['celery_tasks.sms','celery_tasks.email'])