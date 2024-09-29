import urllib
import urllib.request

from django.conf import settings

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


# todo: 临时短信api，等资源下来后替换
def send_sms(phone, sms_code):
    smsapi = "http://api.smsbao.com/"
    # 短信平台账号
    user = settings.SMS_USERNAME
    # 短信平台密码
    password = settings.SMS_PASSWORD
    # 要发送的短信内容
    content = f'【SRE培训学习中心】{sms_code}为您的登录验证码，请于1分钟内填写，如非本人操作，请忽略本短信。'
    data = urllib.parse.urlencode({'u': user, 'p': password, 'm': phone, 'c': content})
    send_url = smsapi + 'sms?' + data
    response = urllib.request.urlopen(send_url)
    status = response.read().decode('utf-8')

    return status
