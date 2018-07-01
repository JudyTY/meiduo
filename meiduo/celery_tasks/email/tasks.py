from django.conf import settings
from django.core.mail import send_mail
from celery_tasks.main import app


@app.task(name='celery_send_email')
def celery_send_email(message, email):
    """
    :param message: token值不固定,需要传参
    :param email: email值不固定,需要传参
    :return:
    """
    header = '美多邮箱激活'
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (email, message, message)
    # 获取django的配置信息需要在main文件中设置将django的配置文件添加环境变量中
    send_mail(subject=header,message='', html_message=html_message, from_email=settings.EMAIL_FROM, recipient_list=[email])
