from .trainer import Trainer
from ..utils import print_progress_bar


class QATrainer(Trainer):
    """
    Allows a chat bot to be trained using a list of strings
    where the list represents a conversation.
    """

    def train(self, conversation, **kwargs):
        """
        {Q:[A1,A2...]}
        Train the chat bot based on the provided list of
        statements that represents a single conversation.
        """
        
         # 匹配一个合适的消息处理器,请务必区分清每个处理器的判断规则，负责只会使用最后一个符合的
        message_adapter = self.matchsys.get_message_adapter(list(conversation.keys())[0])
        statements_to_create = []
        
        for index,item in enumerate(conversation.items()):
            key=item[0]
            value=item[1]
            
            input_statement = message_adapter.process(key,**{'type_of':'Q', 'persona':'user:*'})
            statements_to_create.append(input_statement)
            ans_statements = message_adapter.process_list(value,**{'type_of':'A','persona':'bot:'+self.matchsys.name})
            for ans_statement in ans_statements:
                ans_statement.previous_id = input_statement.previous_id
                statements_to_create.append(ans_statement)
            print_progress_bar(
                    'QA Trainer',
                    index + 1, len(conversation)
            )

        self.matchsys.storage.create_many(statements_to_create)
        self.matchsys.docvector_tool.train(statements_to_create)