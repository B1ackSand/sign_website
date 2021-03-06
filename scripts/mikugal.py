import time
import requests
import random

# 导入tools文件夹下的utils,globalValues
try:
    import tools.utils as tools
    import tools.MD5Encryption as MD5
    import tools.globalValues as gV

except ImportError:
    import sys

    # 可能出现的路径问题，重定向
    sys.path.append('./')
    import tools.utils as tools
    import tools.MD5Encryption as MD5
    import tools.globalValues as gV


# mikugal类
class Mikugal:
    def __init__(self):
        self.session = requests.session()  # 实例化session,跨请求保持参数
        self.name = tools.url_remove_http('FIRST_WEBSITE')  # 访问第一网站
        self.sign_token = None  # token需要记录，以便在addJf确认是否签到成功
        self.date = time.strftime("%Y-%m-%d", time.localtime())  # 记录当天的日期
        self.log_head = f'[{self.date}][{self.name}] '  # log记录头
        self.email = tools.get_environment_variables('MKGAL_EMAIL')  # 邮箱帐号
        self.password = MD5.psw_Encrypt(tools.get_environment_variables('MKGAL_PASSWORD'))  # 帐号密码
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
        try:
            code = self.session.get(tools.get_url_json('FIRST_WEBSITE'), headers=self.headers, timeout=15)
            code.raise_for_status()  # 抛出异常
            tools.send_message(self.log_head + '页面访问正常，状态码：' + str(code.status_code))
            return code.status_code

        #  所有Requests显式抛出的异常都继承自 RequestException
        except requests.exceptions.RequestException as error:
            if self.name != tools.url_remove_http('SECOND_WEBSITE'):
                tools.send_message(self.log_head + '[WARN] 主站访问出错，尝试访问备用站点...')
                self.name = tools.url_remove_http('SECOND_WEBSITE')  # 切换到备用网站进行访问测试
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
        message_context = f'用户名:{response_json["nickname"]} 硬币变化:{response_json["jf"]} + {response_json["qs"]}(非赞助用户为1)'
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
        date = tools.check_signin_status('SIGNIN_DATE')
        status = tools.check_signin_status('SIGNIN_STATUS')

        if response_json['code'] == 0 and date <= self.date and (status == 'success'):
            message_context = f'每日签到成功。\n'
            write_context = {'SIGNIN_DATE': self.date, 'SIGNIN_STATUS': 'success'}
        else:
            if date == self.date and (status == 'success'):
                message_context = f'每日签到失败,你今天签过到了。\n'
                write_context = {'SIGNIN_DATE': self.date, 'SIGNIN_STATUS': 'success'}
            else:
                if (response_json['code'] == 10 or response_json['code'] == 0) and date == self.date and (
                        status == 'fail'):
                    message_context = f'失败后重试签到成功。\n'
                    write_context = {'SIGNIN_DATE': self.date, 'SIGNIN_STATUS': 'success'}
                else:
                    message_context = f'每日签到失败,出现意外的错误。\n'
                    write_context = {'SIGNIN_DATE': self.date, 'SIGNIN_STATUS': 'fail'}
                    gV.Fail_status = True
        tools.write_signin_status(write_context)
        tools.send_message(self.log_head + message_context)  # 信息记录

    def start(self):
        while gV.Fail_status:
            if gV.count >= 5:
                break
            gV.Fail_status = False
            try:
                code = self.test_url_ok()
                if code == requests.codes.ok:
                    self.get_mkgal_sign()
                    self.get_mkgal_addJf()
                gV.count += 1
                time.sleep(3)
            except Exception:
                message_context = f'[ERROR] 运行异常,脚本出现问题！本程序5s后会重试最多5次签到... (已重试'
                tools.send_message(self.log_head + message_context + str(gV.count) + '次)\n')  # 信息log记录
                gV.count += 1
                self.__init__()  # 刷新初始化信息
                self.start()

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
    # 网站更新
    tools.auto_update_website()
    # 签到程序运行
    Mikugal().run()
