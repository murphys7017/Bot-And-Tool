# QQ-Bot-And-Tool
 一个便捷的开发工具组和bot，bot只是附带的[狗头]，目前计划是先实现工具，在开发bot

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

BOT_NAME = 'ALLMIND'
DATA_DIR = r'D:\Code\MyLongTimeProject\A\QQ-Bot-And-Tool\data'

dispatcher = Dispatcher(BOT_NAME,"http://localhost:8882/","ws://localhost:8883/",DATA_DIR)

@dispatcher.QQMessageHandler(identify_value=['测试命令'])
def self_handle(message_info):
    # 自己的处理逻辑
    return '测试命令的响应'


dispatcher.startServer()
~~~



 ## 开发计划

- [x] 尝试使用rasa做消息分发处理
- [ ] 优化rasa的使用
- [ ] 优化整体配置使用
- [ ] 添加新功能

# Parrot

parrot是一个根据群友的历史聊天记录进行回复的脚本。

## 介绍

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

rasa 正在学着做的
