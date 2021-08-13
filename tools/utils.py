import os
import demjson


# 在~/.bash_profile中定义VARIABLE_JSON变量：
# export VARIABLE_JSON='{"MKGAL_EMAIL": "******@***.com", "MKGAL_PASSWORD": "79b87ab**************c6c86ba"}'
# 密码此处为加密，具体实现方式不明，需要通过抓包获得加密后的密码

# 从系统变量中获取VARIABLE_JSON内容
def get_environment_variables(variable_name):
    try:
        return demjson.decode(os.environ['VARIABLE_JSON'])[variable_name]
    except KeyError or OSError:
        send_message('[WARN] 系统环境变量读取失败，尝试从variables.json中读取')
        try:
            with open('variables.json', 'r',
                      encoding='utf-8') as file_object:  # path=~/your/project/path/variables.json
                return demjson.decode(file_object.read())[variable_name]
        except FileNotFoundError:
            send_message('[WARN] 尝试从variables.json中读取失败')


# 记录签到状态
def write_signin_status(context):
    context = demjson.encode(context)
    try:
        with open('sign_status.json', mode='r+', encoding='UTF-8')as file:
            file.seek(0)
            file.truncate()
            file.write(context)
    except IOError:
        print('签到状态记录失败')
        return


# 查询签到状态
def check_signin_status(variable_name):
    try:
        with open('sign_status.json', 'r', encoding='utf-8') as file_object:
            return demjson.decode(file_object.read())[variable_name]
    except Exception:
        print('文件有误，重建文件...')
        context = '{"SIGNIN_DATE": "1970-01-01", "SIGNIN_STATUS": "success"}'
        with open('sign_status.json', mode='w+', encoding='UTF-8')as file:
            file.seek(0)
            file.truncate()
            file.write(context)


# 信息显示和记录
def send_message(context):
    print(context)
    with open('log.txt', mode='a+', newline='\n', encoding='UTF-8')as file:
        file.write(context + '\n')
