


dispatcher = Dispatcher()
storage = Storage()

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
    res = '我在'+message_info['sender.nickname'] + dispatcher.cqCodeBuilder.image(url="D:\Data\Image\emoji\-29af59a4b1fcbc27.gif")
    return res


@dispatcher.QQMessageHandler('give me a wife','随机老婆','给我分配一个老婆吧')
def test_handle(message_info):
    if message_info['message_type'] == 'group':
        user_wifi_id = str(message_info['user_id'])+'-wife'
        res = dispatcher.sendAction('get_group_member_list',{'group_id':message_info['group_id']})
        member_dict = {}
        for member in res['data']:
            if member['card'] == '':
                member['card'] = member['nickname']
            member_dict[member['user_id']] = member
        if user_wifi_id in storage.kv_map:
            return '今天 '+member_dict[storage.get_value(user_wifi_id)]['card']+ '是您的老婆嗷' + dispatcher.cqCodeBuilder.at(wife_key)
        else:
            
            for key in storage.kv_map:
                if key.endswith('-wife'):
                    member_dict.pop(storage.get_value(key))
            wife_key = random.sample(sorted(member_dict.keys()), 1)[0]
            wife = member_dict[wife_key]
            storage.add_map(user_wifi_id,wife['user_id'],1,60*60*24)
            storage.add_map(str(wife_key)+'-wife',wife['user_id'],1,60*60*24)
            return '今天你的老婆是群友：' + member['card'] + '\n' + 'ta的昵称是：' + member['nickname'] + '\n祝99 '+dispatcher.cqCodeBuilder.at(wife_key)
    else:
            return "此功能只对群生效"


dispatcher.startServer()

