import time
import requests
import random
from retrying import retry

# 导入tools文件夹下的utils,globalValues
try:
    import tools.utils as tools
    import tools.globalValues as globalValues
except ImportError:
    import sys

    # 可能出现的路径问题，重定向
    sys.path.append('./')
    import tools.utils as tools
    import tools.globalValues as globalValues


# mikugal类
class Mikugal:
    def __init__(self):
        self.session = requests.session()  # 实例化session,跨请求保持参数
        self.name = 'www.mikugal.com'  # 访问的主网站
        self.sign_token = None  # token需要记录，以便在addJf确认是否签到成功
        self.date = time.strftime("%Y-%m-%d", time.localtime())  # 记录当天的日期
        self.log_head = f'[{self.date}][{self.name}] '  # log记录头
        self.email = tools.get_environment_variables('MKGAL_EMAIL')  # 邮箱帐号
        self.password = tools.get_environment_variables('MKGAL_PASSWORD')  # 帐号密码
        self.headers = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'Sec-Fetch-Dest': 'empty',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.164 Safari/537.36',
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Accept-Language': 'zh-CN,zh;q=0.9,en'}  # headers信息初始化

    # 测试主副网站是否能够正常访问
    def test_url_ok(self):
        url = 'https://' + self.name
        try:
            code = self.session.get(url, headers=self.headers, timeout=15)
            code.raise_for_status()  # 抛出异常
            tools.send_message(self.log_head + '页面访问正常，状态码：' + str(code.status_code))
            return code.status_code

        #  所有Requests显式抛出的异常都继承自 RequestException
        except requests.exceptions.RequestException as error:
            if self.name != 'www.yygal.com':
                tools.send_message(self.log_head + '[WARN] 主站访问出错，尝试访问备用站点...')
                self.name = 'www.yygal.com'  # 切换到备用网站进行访问测试
                self.log_head = f'[{self.date}][{self.name}] '  # 更换头信息
                return self.test_url_ok()
            else:
                tools.send_message(self.log_head + '[ERROR] 访问测试出错,签到失败。')
                raise error  # 抛出异常

    # 编写有关登入的函数
    def get_mkgal_sign(self):
        url = 'https://' + self.name + '/sign'

        # headers格式和data可自己通过简单抓包获得
        h = {
            'Origin': 'https://' + self.name,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://' + self.name + '/'}

        data = {
            'email': self.email,
            'password': self.password}

        # 发送更新后的headers
        headers = self.headers
        headers.update(h)

        # post data过去，内含帐号密码信息
        response = self.session.post(url=url, headers=headers, data=data)
        response_json = response.json()['obj']  # json的obj含有token、昵称和硬币数
        message_context = f'用户名:{response_json["nickname"]} 当前硬币:{response_json["jf"]} + {response_json["qs"]}(or 1)'
        tools.send_message(self.log_head + message_context)  # 记录信息
        self.sign_token = response_json["token"]  # 提取token

    # 编写有关是否签到成功的函数
    def get_mkgal_addJf(self):
        url = 'https://' + self.name + '/addJf'

        # headers格式可自己通过简单抓包获得
        h = {
            'X-Auth-Token': self.sign_token,
            'Referer': 'https://' + self.name + '/'}

        # 发送更新后的headers,获取签到的response
        headers = self.headers
        headers.update(h)

        response = self.session.get(url=url, headers=headers)
        response_json = response.json()

        # response中code显示0（成功）或10（失败或已签过到）
        if response_json['code'] == 0:
            message_context = f'每日签到成功\n'
        else:
            message_context = f'每日签到失败,可能你今天签过到了？\n'
        tools.send_message(self.log_head + message_context)  # 信息记录

    #  运行上面的函数,具有重试机制
    @retry(stop_max_attempt_number=5, wait_fixed=5000)
    def start(self):
        try:
            code = self.test_url_ok()
            if code == requests.codes.ok:
                self.get_mkgal_sign()
                self.get_mkgal_addJf()
        except Exception as error:
            globalValues.count += 1
            message_context = f'[ERROR] 运行异常,脚本出现问题！本程序5s后会重试最多5次签到... (第'
            tools.send_message(self.log_head + message_context + str(globalValues.count) + '次重试)\n')  # 信息log记录
            self.__init__()  # 刷新初始化信息
            raise error

    def run(self):
        # 随机时间
        second = random.randrange(3, 1095, 3)  # 3秒到1095秒之间随机隔3取值,最长时长约19分钟

        # 日志输出
        date_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        tools.send_message(f'[{date_str}]' + ' 随机访问时间为' + str(second) + '秒后...')
        time.sleep(second)  # 休眠second秒后再执行
        date_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        tools.send_message(f'[{date_str}]' + ' 等待结束')
        self.start()


if __name__ == "__main__":
    Mikugal().run()
