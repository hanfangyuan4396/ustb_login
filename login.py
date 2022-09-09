import re
import sys
import configparser
import requests
from wechat_api import WeChatAPI

class Login:
    def __init__(self, wechat_api):
        self.get_ipv6_url = 'http://cippv6.ustb.edu.cn/get_ip.php'
        self.login_url = 'http://202.204.48.66/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64 ) ' +
                          'AppleWebKit/537.36 (KHTML, like Gecko) ' +
                          'Chrome/64.0.3282.186 Safari/537.36'
        }
        self.wechat_api = wechat_api

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
        data = {
            'DDDDD': stuid,
            'upass': pwd,
            '0MKKey': '123456789'
        }
        response = requests.post(url=self.login_url, data=data, headers=self.headers)
        match = re.search('成功', response.text)
        if match:
            print('登录成功!')
            self.wechat_api.send_text_message('登录', '登录成功')
            fee, flow, ip = self.__get_info()
            self.wechat_api.send_text_message('查询', f'余额: {fee}元\n已使用流量: {flow}GB\nip地址: {ip}')
        else:
            print('登录失败!')
            self.wechat_api.send_text_message('登录', '登录失败')


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('login.exe <config_path>')
    else:
        try:
            filenames = sys.argv[1]
            config_parser = configparser.ConfigParser()
            config_parser.read(filenames=filenames)
            CORP_ID = config_parser['wechat']['corporation_id']
            CORP_SECRET = config_parser['wechat']['corporation_secret']
            AGENT_ID = int(config_parser['wechat']['agent_id'])
            STUDENT_ID = config_parser['user']['student_id']
            PASSWORD = config_parser['user']['password']
            wechat_api = WeChatAPI(CORP_ID, CORP_SECRET, AGENT_ID)
            new_login = Login(wechat_api)
            new_login.login(STUDENT_ID, PASSWORD)
        except Exception as e:
            print("发生异常!\n信息:", e)
            wechat_api.send_text_message('发生异常', f'异常信息: {e}')
