from celery import Celery

# 创建celery实例
app = Celery('meiduo')

# 配置
app.config_from_object('celery_tasks.config')

# 自动检索任务
app.autodiscover_tasks(['celery_tasks.sms'])