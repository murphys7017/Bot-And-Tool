import time
import requests
import os
import re
class CqCodeBuilder(object):
    HTTP_SERVER = ''
    TEMP_FILE_DIR = ''
    def __init__(self,url,temp_file):
        self.TEMP_FILE_DIR = temp_file
        if url.endswith('/'):
            self.HTTP_SERVER = url
        else:
            self.HTTP_SERVER = url + '/'
    # TODO: 增强功能，现在只能认为控制url
    def resourceDownload(self,url):
        dirname, filename = os.path.split(url)
        temp_path = os.path.join(self.TEMP_FILE_DIR,filename)
        if '.' not in filename:
            print("请谨慎判断链接是否为文件，如非文件可能造成未知错误")
        if filename in os.listdir(self.TEMP_FILE_DIR):
            return temp_path
        else:
            r = requests.get(url)
            with open(temp_path, "wb") as f:
                f.write(r.content)
                return temp_path
    def sendAction(self,action,params):
        """Send Action
        """
        url = self.HTTP_SERVER + action
        response = requests.get(url, params=params)
        return response.json()
    def baseBuilder(self,type,data):
        res = '[CQ:' + type
        for key in data:
            res = res + ',' + str(key) + '=' + str(data[key])
        res = res + ']'
        return res
    def builder(self,message):
        in_list = re.compile(r'[\[](.*?)[\]]')
        in_list = re.findall(in_list, message)
        for item in in_list:
            message = message.replace('['+item+']', self.image(item))
        return message
    def imageDoCache(self,url):
        data = {}
        data['file'] = 'file:///'+self.resourceDownload(url)
        return self.baseBuilder('image',data)
    def image(self,url,is_flash=False,is_emoji=False):
        data = {}
        if is_flash:
            data['type'] = 'flash'
        if is_emoji:
            data['subType'] = 1
        if url:
            dirname, filename = os.path.split(url)
            data['file'] = filename
            if url.startswith("http://") or url.startswith("https://"):
                data['url'] = url
            else:
                data['url'] = 'file:///'+url
            return self.baseBuilder('image',data)

    def reply(self,reply,message_info):
        data = {
            'id': message_info['message_id'],
            'qq': message_info['self_id'],
            'time': int(round(time.time())*1000),
            'seq': self.sendAction('get_msg',{'message_id': message_info['message_id']})['data']['message_seq']
        }
        return self.baseBuilder('reply',data) + reply

    def poke(self,target):
        return self.baseBuilder('poke',{'qq':target})
    
    def at(self,target):
        return self.baseBuilder('at',{'qq':target})
    
    def record(self,file):
        return self.baseBuilder('record',{'file':file})
    def music(self,type,id):
        return self.baseBuilder('music',{'type':type,'id':id})
    def music_no_type(self,audio,title,image=None,content=None,url=None):
        params = {
            'type': 'custom',
            'url': url,
            'audio': audio,
            'title': title,
            'content': content,
            'image': image

        }
        return self.baseBuilder('music_no_type',params)