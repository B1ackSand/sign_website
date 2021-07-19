import os

SCRIPTS_BASE_DIR = './scripts/'

#  批量运行脚本 if以后有更多脚本
if __name__ == '__main__':
    for scripts in os.listdir(SCRIPTS_BASE_DIR):
        os.system(f'python ./scripts/{scripts}')
