import re
import os
import configparser
import requests
from wechat_api import wechat_api

class Login:
    def __init__(self):
        self.get_ipv6_url = 'http://cippv6.ustb.edu.cn/get_ip.php'
        self.login_url = 'http://202.204.48.66/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64 ) ' +
                          'AppleWebKit/537.36 (KHTML, like Gecko) ' +
                          'Chrome/64.0.3282.186 Safari/537.36'
        }

    def __get_ipv6_address(self):
        ipv6_html = requests.get(self.get_ipv6_url).text
        ipv6_address = ipv6_html[13:].split("'")[0]
        print(ipv6_address)
        return ipv6_address

    def __get_info(self):
        login_success_html = requests.get(url=self.login_url, headers=self.headers).text
        fee = re.search(r"fee='(\d+)", login_success_html).group(1)
        fee = int(fee) / 10000
        flow = re.search(r"flow='(\d+)", login_success_html).group(1)
        flow = int(flow) / (1024 * 1024)
        flow = round(flow, 2)
        ip = re.search(r"v4ip='(.*?)'", login_success_html).group(1)
        print(fee, flow, ip)
        return fee, flow, ip


    def login(self, stuid, pwd):
        ipv6_addr = self.__get_ipv6_address()
        data = {
            'DDDDD': stuid,
            'upass': pwd,
            'v6ip': ipv6_addr,
            '0MKKey': '123456789'
        }
        response = requests.post(url=self.login_url, data=data, headers=self.headers)
        match = re.search('成功', response.text)
        if match:
            print('登录成功!')
            wechat_api.send_text_message('登录', '登录成功')
            fee, flow, ip = self.__get_info()
            wechat_api.send_text_message('查询', f'余额: {fee}元\n已使用流量: {flow}GB\nip地址: {ip}')
        else:
            print('登录失败!')
            wechat_api.send_text_message('登录', '登录失败')


if __name__ == '__main__':
    config_parser = configparser.ConfigParser()
    config_path = os.path.dirname(__file__)
    config_parser.read(filenames=os.path.join(config_path, 'config.ini'))
    STUDENT_ID = config_parser['user']['student_id']
    PASSWORD = config_parser['user']['password']
    try:
        new_login = Login()
        new_login.login(STUDENT_ID, PASSWORD)
    except Exception as e:
        print("发生异常!\n信息:", e)
        wechat_api.send_text_message('发生异常', f'异常信息: {e}')
