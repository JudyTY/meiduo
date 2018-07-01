from django.db import models


# 在公共模块的模型类中设置模型类基类
class BaseModel(models.Model):
    create_date = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    update_date = models.DateTimeField(auto_now=True,verbose_name='更新时间')

    class Meta:

        # 设置为抽象模型类,数据库迁移时不会生成数据表
        abstract = True
