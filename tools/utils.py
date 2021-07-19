import os
import demjson


# 在~/.bash_profile中定义VARIABLE_JSON变量：
# export VARIABLE_JSON='{"MKGAL_EMAIL": "******@***.com", "MKGAL_PASSWORD": "79b87ab**************c6c86ba"}'
# 密码此处为加密，具体实现方式不明，需要通过抓包获得加密后的密码

# 从系统变量中获取VARIABLE_JSON内容
def get_environment_variables(variable_name):
    try:
        return demjson.decode(os.environ['VARIABLE_JSON'])[variable_name]
    except Exception:
        send_message('[WARN] 系统环境变量读取失败，尝试从variables.json中读取')
        with open('variables.json', 'r', encoding='utf-8') as file_object:  # path=~/your/project/path/variables.json
            return demjson.decode(file_object.read())[variable_name]


# 信息显示和记录
def send_message(context):
    print(context)
    with open('log.txt', mode='a+', newline='\n', encoding='UTF-8')as file:
        file.write(context + '\n')
