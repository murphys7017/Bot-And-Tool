import json
import requests
import websocket
import time
import threading
import pandas as pd
import os
import random
import os
from dispatcher import Dispatcher
from parrot import Parrot

# Bot名称
BOT_NAME = 'ALLMIND'
DATA_DIR = r'D:\Code\MyLongTimeProject\A\py\data'


parrot = Parrot(r"D:\Code\MyLongTimeProject\A\py\data\model\test")


class MyDispatch(Dispatcher):
     parrot_run_time = None
     def __init__(self, bot_name , http_server, ws_server, data_path):
          super().__init__(bot_name, http_server, ws_server, data_path)

     def dispatcherServletEndPoint(self,message_info):
        return_message = None
        if message_info['message_type'] == 'private':
            return_message = random.sample(self.fixed_response_map[message_info['message']], 1)[0]
            if return_message is None:
                 return_message = parrot.inferred2string(message_info['message'])
        elif message_info['message_type'] == 'group':
            if self.parrot_run_time:
                 if time.time() - self.parrot_run_time > 10:
                    return_message = parrot.inferred2string(message_info['message'])
                    self.parrot_run_time = time.time()
            else:
                 self.parrot_run_time = time.time()
                 return_message = parrot.inferred2string(message_info['message'])
            if message_info['message'].startswith(self.bot_name):
                message_info['message'] = message_info['message'].split(self.bot_name)[1]
                return_message = random.sample(self.fixed_response_map[message_info['message']], 1)[0]
        if return_message:
            return return_message.replace('{me}',self.bot_name).replace('{name}',message_info['sender']['nickname'])
        else:
            return None


dispatcher = MyDispatch(BOT_NAME,"http://localhost:8882/","ws://localhost:8883/",DATA_DIR)




@dispatcher.QQMessageHandler(identify_type=['commamd'],identify_value=[["Reply Test"]])
def reply_build_test(message_info):
    return dispatcher.cqCodeBuilder.reply("build_test", message_info)

@dispatcher.QQMessageHandler(identify_type=['commamd'],identify_value=[["测试定时任务功能"]])
def add_scheduled_task(message_info):
    lines = message_info['message'].split('\n')
    script_path = ''
    trigger = 'cron'

    month='*' # 月，1-12
    day='*' # 日，1-31
    week='*' # 一年中的第多少周，1-53
    day_of_week='*' # 星期，0-6 或者 mon，tue，wed，thu，fri，sat，sun
    hour=12 # 小时，0-23
    minute=12 # 分，0-59
    second=12 # 秒，0-59
  
    for line in lines:
        if line.startswith('script='):
                script_path = line[7:]
        if line == 'not res':
                need_response = False
        if line.startswith('month='):
                script_path = line[6:]
        if line.startswith('day='):
                script_path = line[4:]
        if line.startswith('dayofweek='):
                script_path = line[10:]
        if line.startswith('week='):
                script_path = line[5:]
        if line.startswith('hour='):
                script_path = line[5:]
        if line.startswith('minute='):
                script_path = line[7:]
        if line.startswith('second='):
                script_path = line[7:]
    dispatcher.addTask("AddTask", minute='*', second='*/20',)
    return

@dispatcher.QQMessageHandler(identify_type=['commamd'],identify_value=[["来个色图","来点色图"]])
def get_some_setu(message_info):
    params = {
        'r18':1,
        'num': 1,
        'tag': []
    }
    for line in message_info['message'].split('\n'):
        if line.endswith('- h'):
            return "使用方式：来点色图\n[tag=tag1 tag2 tag3] \n[]中可以不写，会返回一张色图，从p站下，会比较累"
        if line.startswith('tag='):
            params['tag'] = line[4:].split(' ')
        if line.startswith('r18='):
            params['r18'] = line[4:]
        if line.startswith('num='):
            params['num'] = line[4:]
    if message_info['message_type'] == 'group':
        params['r18'] = 0
    response = requests.get('https://api.lolicon.app/setu/v2', params=params).json()
    response = response['data'][0]['urls']['original']
    return dispatcher.cqCodeBuilder.imageDoCache(response)



@dispatcher.QQMessageHandler(identify_type=['commamd'],identify_value=[[BOT_NAME+'在吗']])
def self_handle(message_info):
    res = '我在'+message_info['sender']['nickname'] + dispatcher.cqCodeBuilder.image(url="D:\Data\Image\emoji\-29af59a4b1fcbc27.gif")
    return res



@dispatcher.QQMessageHandler(identify_value=['测试命令'])
def self_handle(message_info):
    # 自己的处理逻辑
    return '测试命令的响应'




dispatcher.startServer()


