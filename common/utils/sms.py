from typing import List

from django.conf import settings
from tencentcloud.common import credential
from tencentcloud.common.exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.sms.v20210111 import models
from tencentcloud.sms.v20210111 import sms_client as tencent_sms_client
from tencentcloud.sms.v20210111.models import SendStatus


def send_sms(phone, msg):
    """发送短信"""


def send_login_message(phone, sms_code):
    """发送登录验证码短信"""


class SMSClient:
    """
    短信SDK
    """

    TEMPLATE_ID_TO_TEMPLATE = {
        "2330588": "尊敬的讲师，您好！由于培训班取消，您参与的[{1}]已被取消。如有疑问，请随时联系。",
        "2330587": "尊敬的讲师，您好！您负责的培训班[{1}]开始时间已修改，时间由{2}调整为{3}。如有疑问，请随时联系。",
        "2330586": "尊敬的讲师，您好！您负责的培训班[{1}]开始时间已修改。由于您在该时间段已登记不可用时间，我们将另行指定讲师。如有疑问，请随时联系。",
        "2330585": "尊敬的讲师，您好！由于安排调整，您负责的培训班[{1}]被撤销。如有疑问，请随时联系。",
        "2330584": "尊敬的讲师，您好！请您即日起在两天内确认培训班[{1}]的安排。如有疑问，请随时联系。",
        "2330583": "尊敬的讲师，您好！恭喜您被选为[{1}]培训班的讲师。请确认相关安排。如有疑问，请随时联系。",
        "2330582": "尊敬的讲师，您好！您参与的[{1}]培训班已撤销。如有疑问，请随时联系。",
        "2330581": "尊敬的学员，您好！您参与的培训班[{1}]即将考试，考试时间为{2}。请访问以下网址进行考试：{3}。如有疑问，请随时联系。",
        "2329148": "SRE培训学习中心提醒您，{1}为您的登录验证码，请于1分钟内填写，如非本人操作，请忽略本短信。",

    }

    def __init__(self, secret_id: str, secret_key: str, sms_app_id: str, sms_sign_name: str):
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.sms_app_id = sms_app_id
        self.sms_sign_name = sms_sign_name

        # 实例化一个认证对象，入参需要传入腾讯云账户secretId，secretKey。
        # 为了保护密钥安全，建议将密钥设置在环境变量中或者配置文件中。
        # 硬编码密钥到代码中有可能随代码泄露而暴露，有安全隐患，并不推荐。
        # SecretId、SecretKey 查询: https://console.cloud.tencent.com/cam/capi
        # cred = credential.Credential("secretId", "secretKey")
        try:
            cred = credential.Credential(secret_id=self.secret_id, secret_key=self.secret_key)

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
        except TencentCloudSDKException as e:
            self.client = None
            self.error_msg = e

    def send_sms(self, phone_numbers: List[str], template_id: str, template_params: List[str]) -> List[str]:
        """
        发送短信
        :param phone_numbers: 手机列表
        :param template_id: 模板id, 参考类属性TEMPLATE_ID_TO_TEMPLATE
        :param template_params: 参数列表, 填充对应模板中的{1}, {2}, {3} ..., 列表长度和模板占位符一致

        python SDK参考 [https://cloud.tencent.com/document/product/382/43196]
        错误码参考 [https://cloud.tencent.com/document/product/382/38780]
        """
        # if not settings.ENABLE_NOTIFY_SMS:
        #     return []

        if not self.client:
            return [f"无可用sms_client, 检查secret_id和secret_key是否有效, client初始化错误信息: {self.error_msg}"]

        if template_id not in self.TEMPLATE_ID_TO_TEMPLATE:
            return ["模板id无效"]

        req = models.SendSmsRequest()
        req.SmsSdkAppId = self.sms_app_id
        req.SignName = self.sms_sign_name
        req.TemplateId = template_id
        req.TemplateParamSet = template_params
        req.PhoneNumberSet = ["+86" + str(number) for number in phone_numbers]
        req.SessionContext = ""
        req.ExtendCode = ""
        req.SenderId = ""

        resp = self.client.SendSms(req)

        send_status: List[SendStatus] = resp.SendStatusSet
        errors: List[str] = []
        for status in send_status:
            # ---- 发送失败响应体示例 ----
            # {
            #   "SerialNo": "",
            #   "PhoneNumber": "+86xxx",
            #   "Fee": 0,
            #   "SessionContext": "",
            #   "Code": "LimitExceeded.PhoneNumberDailyLimit",
            #   "Message": "the number of sms messages sent from a single mobile number
            #   every day exceeds the upper limit",
            #   "IsoCode": "CN"
            # }

            # ---- 发送成功响应体示例 ----
            # {
            #     "SerialNo": "3363:342902355417337118357899443",
            #     "PhoneNumber": "+86xxx",
            #     "Fee": 1,
            #     "SessionContext": "",
            #     "Code": "Ok",
            #     "Message": "send success",
            #     "IsoCode": "CN"
            # }

            # Fee代表计费条数, 为 0 代表未计费, 没有正确发送出去
            if status.Fee == 0:
                errors.append(f"[{status.PhoneNumber}]发送失败, 状态码: {status.Code}, 错误信息: {status.Message}")

        return errors


sms_client = SMSClient(
    secret_id=settings.SMS_SECRET_ID,
    secret_key=settings.SMS_SECRET_KEY,
    sms_app_id=settings.SMS_APP_ID,
    sms_sign_name=settings.SMS_SIGN_NAME,
)
