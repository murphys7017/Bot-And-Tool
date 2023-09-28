# QQ-Bot-And-Tool

Alice Bot是一个由Aki Polaris 和Murphy共同开发的一个设想很完美的bot，接下来我们也会尽量去完善它。

目前项目只是起步阶段，文档回更新的比较慢，毕竟我平时最讨厌两件事，一件事是写文档，另一件事是写注释。

目前来说完成了基础的底层功能开始设计整个bot了

## 介绍



## 使用

### 依赖

~~~python
websocket # ws客户端
pandas # 读取excel等处理数据
jieba # 分词，模糊匹配
apscheduler # 定时任务
~~~



### 配置

需要go-cqhttp开启正向ws和http接口，工具通过websocket来读取消息，通过http来进行发送消息等操作

### 例子

~~~python
from dispatcher import Dispatcher

BOT_CONFIG = {
    # 必填项
    # 机器人名称（没啥用
    'bot_name' : 'Alice',
    # 保存数据的位置
    'data_path' : r'D:\Code\MyLongTimeProject\A\QQ-Bot-And-Tool\data',
    # gocqhttp的websocket路径和http路径
    'cqhttp_url' : 'http://localhost:8882/',
    'cqws_url' : 'ws://localhost:8883/',
    
    # 可选配置，删除的话即认为不使用对应功能
    'parrot_model_path' : r'D:\Code\MyLongTimeProject\A\QQ-Bot-And-Tool\data\ParrotModel',
    'rasa_url' : 'http://localhost:5005/webhooks/rest/webhook',

}

dispatcher = Dispatcher(BOT_CONFIG)

@dispatcher.QQMessageHandler('测试命令1','测试命令2',...)
def self_handle(message_info):
    # 自己的处理逻辑
    return '测试命令的响应'


dispatcher.startServer()
~~~



# Parrot

parrot是一个根据群友的历史聊天记录进行回复的脚本。

首先明确一下这并不是一个文本生成功能它只是记录群友的发言然后出发时根据相似度来选择合适文本回复的一个功能。

parrot整体原理很简单，将对话数据整理成一个list 然后根据这个list构建一个向量模型，用户输入一句话，找出最相似的list元素的index索引，然后再获取对应的回复

有点难顶，感觉匹配的不算是特别准，先暂时不考虑这个功能了。

## 介绍

### 原理



## 使用

### 依赖

~~~python
jieba
gensim
~~~

### 例子

#### 训练

~~~python
# 请首先确保MODEL_PATH文件夹内有stopwords.txt文件，内为停用词
# 使用list
data =  ['xxxx','xxxx','xxxx',.....]
MODEL_PATH=r"model"
parrot = Parrot(MODEL_PATH)
parrot.train_model(data)

# 使用导出的txt聊天记录
"""导出的格式为这样，如果发生变动请手动处理数据并使用list方式
2023-06-21 1:07:08 昵称(QQ号)
消息

2023-06-21 1:07:15 昵称(QQ号)
消息
"""
file_path = 'path'
parrot.train_model_history(file_path)


# 保存
parrot.save_model(save_path)

# 追加训练
parrot.update_model(['xxxx','xxxx','xxxx',.....])

~~~

#### 对话

~~~~python
MODEL_PATH=r"model"
parrot = Parrot(MODEL_PATH)
return_message = parrot.inferred2string(message)
~~~~



# Rasa

rasa 正在学着做的，好像明白这玩意咋回事了，开始开发功能

## 配置

## 添加对话





# 计划

## RASA

## PARROT



## TOOL

- [ ] 继续优化代码结构添加对群消息和私聊消息之外的其他类型的支持



## BOT

- [ ] 添加随机老婆功能

