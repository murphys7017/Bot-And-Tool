import json
import requests
import websocket
import pandas as pd
import os
import random
import jieba
import re
import difflib
import os
import time
import subprocess

from apscheduler.schedulers.background import BackgroundScheduler
from service.parrot import Parrot
from service.cq_code_builder import CqCodeBuilder
from service import config


CQ_PATTERN = re.compile(r'\[CQ[^\]\[]*\]')


class Dispatcher(object):
    parrot_run_time = None

    bot_name = ''
    fixed_response_map = {}
    user_power_map = {}

    ws_server_path = ""
    http_server_path = ""
    data_path = ''

    similarity_rate = 0.6

    parrot = None
    scheduler = BackgroundScheduler()
    wsapp = object
    cqCodeBuilder = object



    SPECIFIC_MESSAGE_HEADERS = {}
    SCHEDULER_MAP = {}
    GROUP = []
    FRIEND = []
    def __init__(self, if_start_rasa=True):
        config.init()
        self.bot_name = config.SERVICE_CONFIG.bot_name
        self.data_path = config.SERVICE_CONFIG.data_path
        self.http_server_path = config.SERVICE_CONFIG.go_cqhttp_http
        self.ws_server_path = config.SERVICE_CONFIG.go_cqhttp_websocket

        self.cqCodeBuilder = CqCodeBuilder()
        self.scheduler.start()
        self.parrot = Parrot()
            
   
        if if_start_rasa:
                subprocess.Popen('rasa run actions', cwd='./')
                subprocess.Popen('rasa run --enable-api', cwd='./')
        self.init()

    
    def init(self):
        temp_path = os.path.join(self.data_path,'FixedReply')
        for file in os.listdir(temp_path):
            data = pd.read_excel(os.path.join(temp_path,file),header=None, sheet_name=0)
            for index,row in data.iterrows():
                if row[0] in self.fixed_response_map:
                    self.fixed_response_map[row[0]].append(row[1])
                else:
                    self.fixed_response_map[row[0]] = [row[1]]
        

        temp_path = os.path.join(self.data_path,'UserAccessControl')
        for file in os.listdir(temp_path):
            data = pd.read_excel(os.path.join(temp_path,file),header=None, sheet_name=0)
            for index,row in data.iterrows():
                if row[0] in self.user_power_map:
                    self.user_power_map[row[0]] = max(self.user_power_map[row[0]],row[1])
                else:
                    self.user_power_map[row[0]] = row[1]
        
        for item in requests.get(self.http_server_path+'get_group_list').json()['data']:
            self.GROUP.append(item['group_id'])
        
        for item in requests.get(self.http_server_path+'get_friend_list').json()['data']:
            self.FRIEND.append(item['user_id'])


    def dispatcherServletEndPoint(self,message_info):
        """重写如果没有匹配上处理器的最终处理方法,启用rasa,更加智能,但是响应变慢,没有具体到某一个方法的权限管理
        """
        if config.SERVICE_CONFIG.activate_rasa:
            try:
                params = {
                    "sender": message_info['user_id'],
                    "message": message_info['message']
                }
                return_message = requests.post( config.SERVICE_CONFIG.rasa_url, json=params).json()[0]['text']

                if return_message.startswith('PASS'):
                    return_message = None
                else:
                    return return_message
            except:
                pass
        
        if message_info['message_type'] == 'private':
            if message_info['message'] in self.fixed_response_map:
                return_message = random.sample(self.fixed_response_map[message_info['message']], 1)[0]
            if self.parrot and return_message is None:
                return_message = self.parrot.inferred2string(message_info['message'])
        
        elif message_info['message_type'] == 'group':
            if message_info['message'].startswith(self.bot_name):
                message_info['message'] = message_info['message'].split(self.bot_name)[1]
                if message_info['message'] in self.fixed_response_map:
                    return_message = random.sample(self.fixed_response_map[message_info['message']], 1)[0]
            elif self.parrot:
                if self.parrot_run_time:
                    if time.time() - self.parrot_run_time > 10:
                        return_message = self.parrot.inferred2string(message_info['message'])
                        self.parrot_run_time = time.time()
                else:
                    self.parrot_run_time = time.time()
                    return_message = self.parrot.inferred2string(message_info['message'])
        
        if return_message:
            return return_message.replace('{me}',self.bot_name).replace('{name}',message_info['sender']['nickname'])
        else:
            return None
        

    # 消息处理器注解
    # def QQMessageHandler(self,identify_type=[], identify_value=None, identify_level=3):
    #     """声明函数为消息处理函数的注解 @QQMessageHandler(identify_type=[], identify_value=[])
    #     :param identify_type 字符数组  [ 'keywords' , 'similar' , 'commamd' ] 选择使用何种方式来识别命令
    #     :param identify_value 字符数组 [['k1,k2,k3',...] ,[string,...] ,[string,...] ,[string,...]] 具体的值，超出identify_type部分自动归到unknow类，全匹配，可能会影响性能
    #     :param identity_level int 用户权限分级
    #     """
    #     def decorate(fn):
    #         if identify_value is not None:
    #             if identify_level not in self.SPECIFIC_MESSAGE_HEADERS:
    #                 self.SPECIFIC_MESSAGE_HEADERS[identify_level] = {'keywords':{} , 'similar':{} , 'commamd':{},'unknow':{}}
    #             fn.__annotations__['identify_type'] = identify_type
    #             fn.__annotations__['identify_value'] = identify_value
    #             # 在global中添加
    #             j = 0
    #             i = 0
    #             for i in range(len(identify_type)):
    #                 for key in identify_value[i]:
    #                     self.SPECIFIC_MESSAGE_HEADERS[identify_level][identify_type[i]][key] = fn
    #                 j = j + 1
    #             for j in range(j,len(identify_value)):
    #                 for key in identify_value[i]:
    #                     self.SPECIFIC_MESSAGE_HEADERS[identify_level]['unknow'][key] = fn
    #         return fn
    #     return decorate 
    
    def QQMessageHandler(self,*commands, level=5):
        """声明函数为消息处理函数的注解 @QQMessageHandler(identify_type=[], identify_value=[])
        :param identify_type 字符数组  [ 'keywords' , 'similar' , 'commamd' ] 选择使用何种方式来识别命令
        :param identify_value 字符数组 [['k1,k2,much_min_number','k1，k2，much_min_number'...] ,[string,...] ,[string,...] ,[string,...]] 具体的值，超出identify_type部分自动归到unknow类，全匹配，可能会影响性能
        :param identity_level int 用户权限分级
        """
        def decorate(fn):
            if level not in self.SPECIFIC_MESSAGE_HEADERS:
                    self.SPECIFIC_MESSAGE_HEADERS[level] = {}
            
            for key in commands:
                self.SPECIFIC_MESSAGE_HEADERS[level][key] = fn


            return fn
        return decorate 

    # 消息分发到匹配规则的方法
    def messageHandlerMapping(self,message_info):
        """
        划定调用顺序，command精准匹配为最低级
        """
        message = message_info['message']
        default_level = 6
        if message_info['user_id'] in self.user_power_map:
            default_level = self.user_power_map[message_info['user_id']]
        for level in range(default_level+1):
            if level in self.SPECIFIC_MESSAGE_HEADERS:
                for key in self.SPECIFIC_MESSAGE_HEADERS[level]:
                    if str(message).startswith(key):
                        return self.SPECIFIC_MESSAGE_HEADERS[level][key](message_info)
                    elif difflib.SequenceMatcher(lambda x:x in " \t", str(message), key).quick_ratio() > self.similarity_rate:
                        return self.SPECIFIC_MESSAGE_HEADERS[level][key](message_info)
                    elif ',' in key:
                        keys = key.split(',')
                        if len(set(keys[:-1]).intersection(set(jieba.lcut(message)))) > keys[-1:]:
                            return self.SPECIFIC_MESSAGE_HEADERS[level][key](message_info)
                    elif '，' in key:
                        keys = key.split(',')
                        if len(set(keys[:-1]).intersection(set(jieba.lcut(message)))) > keys[-1:]:
                            return self.SPECIFIC_MESSAGE_HEADERS[level][key](message_info)

                # for key in self.SPECIFIC_MESSAGE_HEADERS[level]['similar']:
                #     if difflib.SequenceMatcher(lambda x:x in " \t", str(message), key).quick_ratio() > self.similarity_rate:
                #         return self.SPECIFIC_MESSAGE_HEADERS[level]['similar'][key](message_info)
                
                # for key in self.SPECIFIC_MESSAGE_HEADERS[level]['keywords']:
                #     if len(set(key.split(',')).intersection(set(jieba.lcut(message)))) > 0:
                #         return self.SPECIFIC_MESSAGE_HEADERS[level]['keywords'][key](message_info)
                    
                # for key in self.SPECIFIC_MESSAGE_HEADERS[level]['commamd']:
                #     if str(message).startswith(key):
                #         return self.SPECIFIC_MESSAGE_HEADERS[level]['commamd'][key](message_info)
                
        return None
    
    # 消息加工
    def messageProcesse(self,message_info):
        """消息加工模块，将我们想要的消息进行加工后返回，如果不符合返回None
        """
        message_info = json.loads(message_info)
        if message_info['post_type'] == 'message':
            return message_info
        else:
            print("非MESSAGE EVENT："+message_info)
            return None

    # 消息处理映射器
    def messageDispatcherServlet(self,message_info):
        """将接收到的消息分发到指定的函数处理并将结果返回
        :params wsapp webscoket客户端
        :params message_info 收到的消息
        """
        return_message = None
        message_info = self.messageProcesse(message_info)
        if message_info :
            return_message = self.messageHandlerMapping(message_info)
            # 最终流程
            if return_message is None:
                return_message = self.dispatcherServletEndPoint(message_info)
        else:
            return
        
        if return_message:
            self.sendMessageByMessageInfo(return_message,message_info)
        else:
            return
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