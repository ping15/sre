import urllib
import urllib.request


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


def send_sms(phone, sms_code):
    smsapi = "http://api.smsbao.com/"
    # 短信平台账号
    user = 'gqp_15'
    # 短信平台密码
    password = "dab8292ea8974b64a060c95ad2435206"
    # 要发送的短信内容
    content = f'【SRE培训学习中心】{sms_code}为您的登录验证码，请于1分钟内填写，如非本人操作，请忽略本短信。'
    data = urllib.parse.urlencode({'u': user, 'p': password, 'm': phone, 'c': content})
    send_url = smsapi + 'sms?' + data
    response = urllib.request.urlopen(send_url)
    status = response.read().decode('utf-8')

    return status
