# QQ-Bot-And-Tool

## 开始思考要不要迁移一下

### 前情提要之你怎么知道我买4070了？

### 前情提要

之前的老项目因为被迫沉迷毕设以及找工作，停止了bot的开发，现在工作稳定了（摸鱼摸爽了）决定重新捡起来，目前本项目有以下需要注意的点：

1. 我都用python写了你还跟我谈性能？
2. 项目主打的就是一个未来可期好吧
3. 甭管写的无不无脑，你就说能不能用吧
4. 我都转通信了别对我要求太高

## 介绍

Alice Bot是一个由Aki Polaris 和Murphy共同开发的一个设想很完美的bot，接下来我们也会尽量去完善它。

目前项目只是起步阶段，文档回更新的比较慢，毕竟我平时最讨厌两件事，一件事是写文档，另一件事是写注释。

目前来说完成了基础的底层功能开始设计整个bot了

全新的Alice其实核心内容是快速开发框架，曾经尝试参考Spring MVC的原理来做，但是看了开头我就意识到，我已经不是以前那个啥都能干的我了，遂这个框架写的有亿点简陋，不过因为工作比较闲，肯定是会继续完善的。

## 使用

### 依赖

~~~python
websocket # ws客户端
pandas # 读取excel等处理数据
jieba # 分词，模糊匹配
apscheduler # 定时任务
jionlp # 工具集，计划用，但是基本没用
rasa # 3以上，可选
~~~



### 配置

需要go-cqhttp开启正向ws和http接口，工具通过websocket来读取消息，通过http来进行发送消息等操作

> 可自行重写`dispatcher`中的`messageProcesse`方法和`sendAction`方法来进行适配其他数据源
>
> 非web socket可以直接调用`messageDispatcherServlet`

**`message_info`参数格式要求：**

~~~python
{
  'post_type': 'message', 
  'message_type': 'private', 
  'time': 1694183059, 
  'self_id': 2762018040, 
  'sub_type': 'friend', 
  'target_id': 2762018040, 
  'message': '你好', 
  'font': 0, 
  'sender': {'age': 0, 'nickname': 'Aki-Polaris', 'sex': 'unknown', 'user_id': xxx}, 
  'message_id': -2001115448, 
  'user_id': xxx
}

{
  'post_type': 'message', 
  'message_type': 'group', 
  'time': 1694395091, 
  'self_id': xxx, 
  'sub_type': 'normal', 
  'anonymous': None, 
  'message': '', 
  'message_seq': 81567, 
  'font': 0, 
  'group_id': xxx, 
  'sender': {'age': 0, 'area': '', 'card': '', 'level': '', 'nickname': 'xxx', 'role': 'member', 'sex': 'unknown', 'title': '', 'user_id': xxx}, 
  'user_id': xxx, 
  'message_id': -185279243
}
~~~





### 例子

**config.yml**

~~~yml
# 同bot名称
assistant_id: Alice
# 和风api的用户key
he_feng_key: 4fd5b28a9a27428e92dd14cada996806
go_cqhttp_http: http://localhost:8882/
go_cqhttp_websocket: ws://localhost:8883/
~~~

**main.py**

~~~python
from dispatcher import Dispatcher

dispatcher = Dispatcher()

@dispatcher.QQMessageHandler('测试命令1','测试命令2',...)
def self_handle(message_info):
    # 自己的处理逻辑
    return '测试命令的响应'


dispatcher.startServer()
~~~



# Parrot

引入了chatterbot，不过是私人魔改版，大抵是不好使的，

## 目前因为群友聊天太混乱了，还在思考该怎么设计合理一些

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

- [x] 添加天气
- [x] 添加色图
- [ ] 将随机老婆迁移到这里

## PARROT

- [ ] 扩大数据集重新训练

## TOOL

- [x] 继续优化代码结构添加对群消息和私聊消息之外的其他类型的支持
- [x] 优化配置文件，还有一部分可以添加到配置文件中
- [ ] 整合优化chatterbot


## BOT

- [x] 添加随机老婆功能

