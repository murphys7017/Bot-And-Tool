from .trainer import Trainer
from ..utils import print_progress_bar


class ChatListTrainer(Trainer):
    """
    
    Allows a chat bot to be trained using a list of strings
    where the list represents a conversation.

    [[...][...][...]...][0]
            ↓
            [  
                xxx.{xxx} :persona
                xxx
                xxx
                xxx
                xxx
                xxx
                xxx
            ]
    """

    def train(self, conversation, **kwargs):
        
         # 匹配一个合适的消息处理器,请务必区分清每个处理器的判断规则，负责只会使用最后一个符合的
        message_adapter = self.matchsys.get_message_adapter(conversation[0][0])
        statements_to_create = []
        
        for index,chain in enumerate(conversation):
        
            statements = message_adapter.process_list(chain,**{'type_of':'CHAT','persona':'*'})
            statements[0].next_id = statements[1].id
            for i in range(1,len(statements)-1):
                statements[i].previous_id = statements[i-1].id
                statements[i].next_id = statements[i+1].id
            statements[len(statements)-1].previous_id = statements[len(statements)-2].id
            print_progress_bar(
                'Chat Trainer',
                index + 1, len(conversation)
            )
            statements_to_create = statements_to_create + statements
        print(statements_to_create)
        self.matchsys.storage.create_many(statements_to_create)
        self.matchsys.docvector_tool.train(statements_to_create)