import requests
import websocket
import pandas as pd
from pandas import json_normalize
import os
import random
import jieba
import re
import difflib
import os
import time
import subprocess
import json

from apscheduler.schedulers.background import BackgroundScheduler
from service.parrot import Parrot
from service.cq_code_builder import CqCodeBuilder
from service import config
config.initialize()

CQ_PATTERN = re.compile(r'\[CQ[^\]\[]*\]')


class Dispatcher(object):
    parrot_run_time = None

    bot_name = ''
    fixed_response_map = {}
    user_power_map = {}

    ws_server_path = ""
    http_server_path = ""
    data_path = ''

    command_similarity_rate = 0.6

    parrot = None
    scheduler = BackgroundScheduler()
    wsapp = object
    cqCodeBuilder = object



    command_index = {}
    SCHEDULER_MAP = {}
    GROUP = []
    FRIEND = []
    def __init__(self,parrot_similarity_rate=0.92):
        self.bot_name = config.bot_name
        self.data_path = config.data_path
        self.http_server_path = config.go_cqhttp_http
        self.ws_server_path = config.go_cqhttp_websocket
        self.command_similarity_rate = config.command_similarity_rate

        self.cqCodeBuilder = CqCodeBuilder()
        self.scheduler.start()
        if parrot_similarity_rate is None:
            self.parrot = None
        else:
            self.parrot = Parrot(parrot_similarity_rate)
   
        if config.if_start_rasa:
                subprocess.Popen('rasa run actions', cwd='./')
                subprocess.Popen('rasa run --enable-api', cwd='./')
        self.init()

    
    def init(self):
        # 加载固定回复
        if self.parrot is None:
            self.parrot = {}
            temp_path = os.path.join(self.data_path,'FixedReply')
            for file in os.listdir(temp_path):
                data = pd.read_excel(os.path.join(temp_path,file),header=None, sheet_name=0)
                for index,row in data.iterrows():
                    if row[0] in self.parrot:
                        self.parrot[row[0]].append(row[1])
                    else:
                        self.parrot[row[0]] = [row[1]]
        

        # 用户权限读取
        temp_path = os.path.join(self.data_path,'UserAccessControl')
        for file in os.listdir(temp_path):
            data = pd.read_excel(os.path.join(temp_path,file),header=None, sheet_name=0)
            for index,row in data.iterrows():
                if row[0] in self.user_power_map:
                    self.user_power_map[row[0]] = max(self.user_power_map[row[0]],row[1])
                else:
                    self.user_power_map[row[0]] = row[1]
        
        # 群列表和用户表
        for item in requests.get(self.http_server_path+'get_group_list').json()['data']:
            self.GROUP.append(item['group_id'])
        
        for item in requests.get(self.http_server_path+'get_friend_list').json()['data']:
            self.FRIEND.append(item['user_id'])

    def getRasaResponse(self,message_info):
        
        try:
            params = {
                "sender": str(message_info['user_id']),
                "message": message_info['message']
            }
  
            return_message = requests.post( config.SERVICE_CONFIG.rasa_url, json=params).json()[0]['text']

            if return_message.startswith('PASS'):
                return_message = None
            elif return_message.startswith('RASA_RUN_FUNCTION_By_COMMAND:'):
                return_message = self.messageHandlerMapping(message_info)
            else:
                return return_message
        except Exception as e:
            print(e)
            return None
    
    def fixReponseParrot(self,message_info):
        return_message = None
        if message_info['message_type'] == 'private':
                if type(self.parrot) is Parrot:
                    return_message = random.sample(self.parrot.inferred2string(message_info['message']), 1)[0]
                else:
                    if message_info['message'] in self.parrot:
                        return_message = random.sample(self.parrot[message_info['message']], 1)[0]

        elif message_info['message_type'] == 'group':
            if message_info['message'].startswith(self.bot_name):
                message_info['message'] = message_info['message'].split(self.bot_name)[1]
                if type(self.parrot) is Parrot:
                    return_message = random.sample(self.parrot.inferred2string(message_info['message']), 1)[0]
                else:
                    if message_info['message'] in self.parrot:
                        return_message = random.sample(self.parrot[message_info['message']], 1)[0]

        return return_message

    def dispatcherServletEndPoint(self,message_info):
        """重写如果没有匹配上处理器的最终处理方法,启用rasa,更加智能,但是响应变慢,没有具体到某一个方法的权限管理
        """
        return_message = None
        if config.SERVICE_CONFIG.activate_rasa:
            return_message = self.getRasaResponse(message_info)
        
        if return_message is None:
            return_message = self.fixReponseParrot(message_info)
        
        if return_message:
            return return_message.replace('{me}',self.bot_name).replace('{name}',message_info['sender.nickname'])
        else:
            return None
    
    def QQMessageHandler(self,*commands, level=5, activate_id=None):
        """声明函数为消息处理函数的注解 @QQMessageHandler
        """
        def decorate(fn):
   
            for key in commands:
                self.command_index[key] = {
                    'function' : fn,
                    'activate_id' : activate_id,
                    'level' : level
                }
                
            return fn
        return decorate 
    

    # 获取用户权限
    def getUserPower(self,message_info):
        # 用户权限
        if message_info['user_id'] in self.user_power_map:
            return self.user_power_map[message_info['user_id']]
        else:
            return 3
    
    # 根据消息获取到方法的索引
    def getCommandByMessage(self,message_info,user_power):
        message = message_info['message']
        for key in self.command_index:
            if user_power >= self.command_index[key]['level']:
                # 匹配消息的开头
                if str(message).startswith(key):
                    return key
                
                    # 匹配相似度 计划废弃
                elif difflib.SequenceMatcher(lambda x:x in " \t", str(message), key).quick_ratio() > self.command_similarity_rate:
                    return key
                    
                    # 匹配关键词 计划废弃
                elif ',' in key:
                    keys = key.split(',')
                    if len(set(keys[:-1]).intersection(set(jieba.lcut(message)))) > keys[-1:]:
                            return key
                elif '，' in key:
                    keys = key.split(',')
                    if len(set(keys[:-1]).intersection(set(jieba.lcut(message)))) > keys[-1:]:
                        return key
            elif self.command_index[key]['activate_id'] is not None:
                if message_info['user_id'] in self.command_index[key]['activate_id']:
                    return key
        return None

    # 调用方法执行
    def runAction(self, command,message_info):
        print("runAction")
        return self.command_index[command]['function'](message_info)
        
            
    # 消息分发到匹配规则的方法
    def messageHandlerMapping(self,message_info):
        """
        划定调用顺序，command精准匹配为最低级
        """
        user_power = self.getUserPower(message_info)
        command = self.getCommandByMessage(message_info,user_power)
        if command:
            return self.runAction(command,message_info)

        return None
    
    # 消息加工
    def messageProcesse(self,message_info):
        """消息加工模块，将我们想要的消息进行加工后返回，如果不符合返回None
        """
        message_info = json.loads(message_info)
        message_info = json_normalize(message_info).loc[0]
        if message_info['post_type'] == 'message':
            return message_info
        else:
            print("非MESSAGE EVENT："+message_info.to_json())
            return None
    
    def textMesssageBuilder(self, message:str,message_info):
        # {message_info_key}
        in_list = re.compile(r'[\{](.*?)[\}]')
        in_list = re.findall(in_list, message)
        for key in in_list:
            if key in message_info:
                message = message.replace(key, message_info[key])
        return message
    # 消息处理映射器
    def messageDispatcherServlet(self,message_info):
        """将接收到的消息分发到指定的函数处理并将结果返回
        :params wsapp webscoket客户端
        :params message_info 收到的消息
        """
        return_message = None
        message_info = self.messageProcesse(message_info)
        if message_info is not None:
            return_message = self.messageHandlerMapping(message_info)
            # 最终流程
            if return_message is None:
                return_message = self.dispatcherServletEndPoint(message_info)
        
        if return_message:
            # {message_info_key}
            return_message = self.textMesssageBuilder(return_message,message_info)
            self.sendMessageByMessageInfo(return_message,message_info)
            return True
        else:
            return False
    def sendMessageByMessageInfo(self,message,message_info):
        """Send a message
        """
        if message_info['message_type'] == 'private':
            self.sendPrivateMessage(message,message_info['user_id'])
        elif message_info['message_type'] == 'group':
            self.sendGroupMessage(message,message_info['group_id'])

    def SendMessageByTarget(self,message,target):
        if target in self.FRIEND:
            self.sendPrivateMessage(message,target)
        if target in self.GROUP:
            self.sendGroupMessage(message,target)
    def sendPrivateMessage(self,message,target):
        params={
                "message": message,
                "user_id": target,
                'message_type': 'private'
        }
        self.sendAction('send_msg',params)
    def sendGroupMessage(self,message,target):
        params={
                "message": message,
                "group_id": target,
                'message_type': 'group'
        }
        self.sendAction('send_msg',params)

    def sendAction(self,action,params):
        """Send Action
        """
        url = self.http_server_path + action
        response = requests.get(url, params=params)
        return response.json()
    def taskExecutor(self,context,target):
        if os.path.isfile(self.data_path + '/script/'+context):
            f = os.popen(self.data_path + '/script/'+context, 'r')
            res = f.readlines()		# res接受返回结果
            f.close()
            if res[0].startswith('response:'):
                self.SendMessageByTarget(res,target)
        else:
            self.SendMessageByTarget(context,target)
    # TODO: 太麻烦了等什么时候想到好的处理方式了再搞
    def addTask(self,
                 content,
                 target,
                 trigger='cron',
                 month='*', # 月，1-12
                 day='*', # 日，1-31
                 week='*', # 一年中的第多少周，1-53
                 day_of_week='*',
                 hour='*', # 小时，0-23
                 minute=12, # 分，0-59
                 second=12 # 秒，0-59
                ):
        task_id = str(str(target)+content[:5])
        if task_id in self.SCHEDULER_MAP:
            self.SCHEDULER_MAP[task_id].remove()
            self.SendMessageByTarget("Task ID:"+task_id+"\n已移除此任务。",target)
            return 
      
      
        job = self.scheduler.add_job(
                    self.task_executor,
                    args=[content,target],
                    trigger=trigger,
                    month=month,
                    day=day,
                    week=week,
                    day_of_week=day_of_week,
                    hour=hour,
                    minute=minute,
                    second=second
            )
        self.SCHEDULER_MAP[task_id] = job
        self.SendMessageByTarget("Task ID:"+task_id+"\n创建完成，再次发送将移除此任务。",target=target)
    


    def onOpen(self,wsapp):
        print("on_open")

    def onMessage(self,wsapp, message_info):
        self.messageDispatcherServlet(message_info)


    def onClose(self,wsapp):
        print("on_close")

    def startServer(self):
        self.wsapp = websocket.WebSocketApp(self.ws_server_path,on_open=self.onOpen,on_message=self.onMessage,on_close=self.onClose)
        self.wsapp.run_forever()