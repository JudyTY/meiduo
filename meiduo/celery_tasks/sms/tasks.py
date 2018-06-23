from celery_tasks.sms.yuntongxun.sms import CCP
from . import constants
from celery_tasks.main import app


@app.task()
def send_sms_code(mobile, num):
    # 2.2 调用接口发送数据
    # ccp = CCP()
    # time = str(constants.SMS_CODE_REDIS_EXPIRES / 60)
    # ccp.send_template_sms(mobile, ["%06d" % num, time], constants.SMS_TEMP_ID)
    print(num)
