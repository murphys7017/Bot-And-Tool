# Bot-And-Tool Parrot
从一开始的就是单纯的给函数一个注解然后去根据消息调用函数生成响应
到添加了固定回复功能
再到引入doc2vec进行向量化预测匹配
再到现在的快要成形的，消息接收，搜索匹配，逻辑处理，响应生成多个模块

目前项目只是起步阶段，文档更新的比较慢，毕竟我平时最讨厌两件事，一件事是写文档，另一件事是写注释。

目前来说完成了基础的底层功能开始设计整个bot了

从今天开始这个项目将不在含有QQ部分，等局势好转后在考虑适配了。
其实这个做这个项目一开始想的是在尽可能低占用的情况下来实现一个功能较为丰富的bot，但是我选择了使用python作为开发语言，所以已经不关心占用了，后续基本完成后可能会迁移到go。
目前这个项目暂定的名字是Parrot，他本质上就是一个复读机，顶多是讲点逻辑的复读机，并不想上生成式的Ai模型，对我来说的占用太高了。

之前的老项目因为被迫沉迷毕设以及找工作，停止了bot的开发，现在工作稳定了（摸鱼摸爽了）决定重新捡起来，目前本项目有以下需要注意的点：

1. 我都用python写了你还跟我谈性能？
2. 项目主打的就是一个未来可期好吧
3. 甭管写的无不无脑，你就说能不能用吧
4. 我都转通信了别对我要求太高


## 项目结构
项目的核心其实就是MatchSys文件夹，其他的算是我不断尝试各种库和方法遗留的一些代码之类的。
整个项目分为训练、消息处理、相似对话搜索、对搜索结果的逻辑处理、数据存储、工具类、以及主程序和一些其他的代码
### trainer
此模块主要作用是将对话数据添加到数据库和模型中，目前只实现了QA对话，后续继续实现短对话。
自定义训练必须继承`Trainer`实现`train`函数最好也把`save`函数一起实现了
使用方式
~~~python
from service.MatchSys import MatchSys
ms = MatchSys()
import pandas as pd
# QA {Q：{A1，A2...} ...}
map = {}

from service.MatchSys.trainer import QATrainer
trainer = QATrainer(ms)
trainer.train(map)
~~~

### message
message的核心作用就是把接收到的消息转换成标准的statement形式，把statement输出成需要的形式

### search
search主要是找出和输入的statement相似的已经保存到数据库中的statement数据，核心是训练好的doc2vec模型，使用doc2vec获得相似的id

### logic
此模块主要的作用就是对搜索的statement结果列表进行处理选择一个合适的statement返回
可以在创建MatchSys时logic_adapter_name_list使用指定使用的逻辑处理器列表，默认使用`service.MatchSys.logic.BestMatch`，可以指定多个逻辑处理器
自己的逻辑处理器必须得继承`LogicAdapter`实现`process`和`default_responses_process`两个函数




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







# 计划

- [ ] 添加短对话训练器
- [ ] 添加使用GPU训练模型
- [ ] 添加根据意图匹配，提升匹配精度 **计划下一步开发**
- [ ] 意图数据表与对话数据表关联
- [ ] 添加从对话中学习
<<<<<<< Updated upstream
- [ ] 不同角色的搜索
=======
- [ ] 对话中的命名实体替换了优化匹配效果
- [ ] 优化函数的触发方法
>>>>>>> Stashed changes
- [x] 添加天气
- [x] 添加色图
- [ ] 将随机老婆迁移到这里
- [ ] 扩大数据集重新训练
- [x] 继续优化代码结构添加对群消息和私聊消息之外的其他类型的支持
- [x] 优化配置文件，还有一部分可以添加到配置文件中
- [ ] 添加随机老婆功能

