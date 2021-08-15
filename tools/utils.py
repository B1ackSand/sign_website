import os
import demjson
import requests
from bs4 import BeautifulSoup


# 在~/.bash_profile中定义VARIABLE_JSON变量：
# export VARIABLE_JSON='{"MKGAL_EMAIL": "******@***.com", "MKGAL_PASSWORD": "79b87ab**************c6c86ba"}'
# 网站会对密码进行加密，具体实现方式为MD5加密

# 从系统变量中获取VARIABLE_JSON内容
def get_environment_variables(variable_name):
    try:
        return demjson.decode(os.environ['VARIABLE_JSON'])[variable_name]
    except KeyError or OSError:
        send_message('[WARN] 系统环境变量读取帐号或密码失败，尝试从variables.json中读取')
        try:
            with open('variables.json', 'r',
                      encoding='utf-8') as file:  # path=~/your/project/path/variables.json 根目录
                return demjson.decode(file.read())[variable_name]
        except FileNotFoundError:
            send_message('[WARN] 尝试从variables.json中读取失败')


# 记录签到状态
def write_signin_status(context):
    try:
        with open('sign_status.json', mode='r+', encoding='UTF-8') as file:
            demjson.encode_to_file('sign_status.json', context, overwrite=True)
    except IOError:
        print('签到状态记录失败')
        return


# 查询签到状态
def check_signin_status(variable_name):
    try:
        with open('sign_status.json', 'r', encoding='UTF-8') as file:
            value = demjson.decode(file.read())[variable_name]
            file.close()
            return value
    except Exception:
        print('文件有误，重建文件...')
        context = '{"SIGNIN_DATE": "1970-01-01", "SIGNIN_STATUS": "success"}'
        with open('sign_status.json', mode='w+', encoding='UTF-8') as file:
            demjson.encode_to_file('sign_status.json', context, overwrite=True)


# 信息显示和记录
def send_message(context):
    print(context)
    with open('log.txt', mode='a+', newline='\n', encoding='UTF-8') as file:
        file.write(context + '\n')


# 获取json中url地址
def get_url_json(variable_name):
    try:
        with open('website.json', 'r+', encoding='UTF-8') as file:
            return demjson.decode(file.read())[variable_name]
    except FileNotFoundError or KeyError:
        send_message('[WARN] 尝试从website.json中读取数据失败')


# 在json写入最新url
def write_latest_url(order, latest_url):
    try:
        with open('website.json', mode='r+', encoding='UTF-8') as file:
            json_object = demjson.decode(file.read())
            json_object[order] = latest_url
            demjson.encode_to_file('website.json', json_object, overwrite=True)
            send_message('网站已更新为:' + str(latest_url))
    except IOError or FileNotFoundError:
        send_message('[WARN] 尝试从website.json中写入数据失败')
        return


# 自动更新url
def auto_update_website():
    print('现在开始对签到网站URL进行更新...')
    target = 'https://xygalgame.com/'
    req = requests.get(url=target)
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    soup = soup.find_all('h2')
    if get_url_json('FIRST_WEBSITE') != soup[1].contents[0]:
        write_latest_url('FIRST_WEBSITE', soup[1].contents[0])
    if get_url_json('SECOND_WEBSITE') != soup[0].contents[0]:
        write_latest_url('SECOND_WEBSITE', soup[0].contents[0])
    print('更新完成。')


# url修正，用于mikugal获取无“http”前缀的网站
def url_remove_http(variable_name):
    url = get_url_json(variable_name)
    remove_part = 'https://'
    return url.lstrip(remove_part)
