# 此文件用来捕获数据库异常和redis异常
import logging

from django.db import DatabaseError
from redis import RedisError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler
# 获取配置文件中新定义的django日志器
logger = logging.getLogger('django')


def exception_handler(exc,context):
    """
    自定义处理异常
    :param exc: 异常
    :param context: 抛出异常的上下文
    :return: Response响应对象
    """

    # 调用DRF原声的异常处理函数
    response = drf_exception_handler(exc,context)
    view = context['view']
    if response is None:
        # 如果DRF框架没有捕获到本次错误,则: 1. 没有错误 2. 数据库错误
        if isinstance(exc,DatabaseError) or isinstance(exc,RedisError):
            # 数据库异常
            logger.error('[%s] %s' % (view, exc))
            response = Response({'message':'服务器内部错误'},status=status.HTTP_507_INSUFFICIENT_STORAGE)

    return response