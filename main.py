from dispatcher import Dispatcher


BOT_CONFIG = {
    'bot_name' : 'Alice',
    'data_path' : r'D:\Code\MyLongTimeProject\A\QQ-Bot-And-Tool\data',
    'cqhttp_url' : 'http://localhost:8882/',
    'cqws_url' : 'ws://localhost:8883/',
    'parrot_model_path' : r'D:\Code\MyLongTimeProject\A\QQ-Bot-And-Tool\data\ParrotModel',
    'rasa_url' : 'http://localhost:5005/webhooks/rest/webhook',

}


dispatcher = Dispatcher(BOT_CONFIG)


@dispatcher.QQMessageHandler('reply_build_test')
def reply_build_test(message_info):
    return dispatcher.cqCodeBuilder.reply("build_test", message_info)


@dispatcher.QQMessageHandler("测试定时任务功能")
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




@dispatcher.QQMessageHandler('Alice在吗')
def self_handle(message_info):
    res = '我在'+message_info['sender']['nickname'] + dispatcher.cqCodeBuilder.image(url="D:\Data\Image\emoji\-29af59a4b1fcbc27.gif")
    return res


@dispatcher.QQMessageHandler('测试命令')
def test_handle(message_info):
    # 自己的处理逻辑
    return '测试命令的响应'


dispatcher.startServer()


