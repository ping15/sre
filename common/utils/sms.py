import urllib
import urllib.request
from typing import List

from django.conf import settings
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.sms.v20190711 import sms_client as tencent_sms_client

status_mapping = {
    '0': '短信发送成功',
    '-1': '参数不全',
    '-2': '服务器空间不支持,请确认支持curl或者fsocket,联系您的空间商解决或者更换空间',
    '30': '密码错误',
    '40': '账号不存在',
    '41': '余额不足',
    '42': '账户已过期',
    '43': 'IP地址限制',
    '50': '内容含有敏感词'
}

SUCCESS_STATUS = "0"


# todo: 临时短信api，等资源下来后替换
def send_sms(phone, msg):
    """发送短信"""
    smsapi = "http://api.smsbao.com/"
    # 短信平台账号
    user = settings.SMS_USERNAME
    # 短信平台密码
    password = settings.SMS_PASSWORD
    # 要发送的短信内容
    content = msg
    data = urllib.parse.urlencode({'u': user, 'p': password, 'm': phone, 'c': content})
    send_url = smsapi + 'sms?' + data
    response = urllib.request.urlopen(send_url)
    status = response.read().decode('utf-8')

    return status


def send_login_message(phone, sms_code):
    """发送登录验证码短信"""
    send_sms(phone, f'【SRE培训学习中心】{sms_code}为您的登录验证码，请于1分钟内填写，如非本人操作，请忽略本短信。')


class SMSClient:
    """
    短信SDK
    """

    TEMPLATE_ID_TO_TEMPLATE = {
        "2322925": "尊敬的学员，您好！您参与的课程[{1}]即将考试，考试时间为{2}。请访问以下网址进行考试：{3}。如有疑问，请随时联系。",
        "2322924": "尊敬的讲师，您好！您参与的[{1}]课程已撤销。如有疑问，请随时联系。",
        "2322923": "尊敬的讲师，您好！恭喜您被选为[{1}]课程的讲师。请确认相关安排。如有疑问，请随时联系。",
        "2322922": "尊敬的讲师，您好！请您即日起在两天内确认课程[{1}]的安排。如有疑问，请随时联系。",
        "2322920": "尊敬的讲师，您好！由于安排调整，您负责的课程[{1}]被撤销。如有疑问，请随时联系。",
        "2322919": "尊敬的讲师，您好！您负责的课程[{1}]开课时间已修改。由于您在该时间段已登记不可用时间，"
                   "我们将另行指定讲师。如有疑问，请随时联系",
        "2322918": "尊敬的讲师，您好！您负责的课程[{1}]开课时间已修改，时间由{2}调整为{3}。如有疑问，请随时联系。",
        "2322916": "尊敬的讲师，您好！由于培训班取消，您参与的[{1}]已被取消。如有疑问，请随时联系。",
    }

    def __init__(self, secret_id: str, secret_key: str):
        # 实例化一个认证对象，入参需要传入腾讯云账户secretId，secretKey。
        # 为了保护密钥安全，建议将密钥设置在环境变量中或者配置文件中。
        # 硬编码密钥到代码中有可能随代码泄露而暴露，有安全隐患，并不推荐。
        # SecretId、SecretKey 查询: https://console.cloud.tencent.com/cam/capi
        # cred = credential.Credential("secretId", "secretKey")
        try:
            cred = credential.Credential(secret_id=secret_id, secret_key=secret_key)

            # 实例化一个http选项，可选的，没有特殊需求可以跳过。
            http_profile = HttpProfile()
            # 如果需要指定proxy访问接口，可以按照如下方式初始化hp（无需要直接忽略）
            # httpProfile = HttpProfile(proxy="http://用户名:密码@代理IP:代理端口")
            http_profile.reqMethod = "POST"  # post请求(默认为post请求)
            http_profile.reqTimeout = 10  # 请求超时时间，单位为秒(默认60秒)
            http_profile.endpoint = "sms.tencentcloudapi.com"  # 指定接入地域域名(默认就近接入)

            # 非必要步骤:
            # 实例化一个客户端配置对象，可以指定超时时间等配置
            client_profile = ClientProfile()
            client_profile.signMethod = "TC3-HMAC-SHA256"  # 指定签名算法
            client_profile.language = "en-US"
            client_profile.httpProfile = http_profile

            # 实例化要请求产品(以sms为例)的client对象
            # 第二个参数是地域信息，可以直接填写字符串ap-guangzhou，
            # 支持的地域列表参考 https://cloud.tencent.com/document/api/382/52071#.E5.9C.B0.E5.9F.9F.E5.88.97.E8.A1.A8
            self.client = tencent_sms_client.SmsClient(cred, "ap-guangzhou", client_profile)
            self.error_msg = ""
        except Exception as e:
            self.client = None
            self.error_msg = e

    def send_sms(self, phones: List[str]):
        pass


sms_client = SMSClient(secret_id=settings.SMS_SECRET_ID, secret_key=settings.SMS_SECRET_KEY)
