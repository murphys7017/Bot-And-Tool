import sys
sys.path.append(r"C:\Users\Administrator\Documents\GitHub\QQ-Bot-And-Tool") 

from MatchSys import MatchSys
ms = MatchSys(
        name='teat_sys',
        ltp_model_path=r'data\LtpModel',
        database_uri='sqlite:///data/db.sqlite3',
        text_vec_model_path=r'data\model.bin',
        vector_similarity_rate=0.7,
        most_similar_number=10,
        vector_match_times=5,

    )
from MatchSys.trainer.base_chat_list_trainer import ChatListTrainer

trainer = ChatListTrainer(ms)


data = [
    [
        '可战争在哪儿？现在全球一处热点都没有，应该是历史上最和平的年代了。',
        '没有。',
        '那你的生活是一种偶然，世界有这么多变幻莫测的因素，你的人生却没什么变故。',
        '大部分人都是这样嘛。',
        '那大部分人的人生都是偶然。',
        '可......多少代人都是这么平淡地过来的。',
        '都是偶然。',
        '得承认今天我的理解力太差了，您这岂不是说......',
        '是的，整个人类历史也是偶然，从石器时代到今天，都没什么重大变故，真幸运。但既然是幸运，总有结束的一天；现在我告诉你，结束了，做好思想准备吧。',
    ]
]
        
trainer.train(data)