from .trainer import Trainer
from ..utils import print_progress_bar


class QATrainer(Trainer):
    """
    Allows a chat bot to be trained using a list of strings
    where the list represents a conversation.
    """
    def build_line_relations(self, statements):
        pass
        # statements[0].next_id = statements[1].id
        # for i in range(1,len(statements)-1):
        #     statements[i].previous_id = statements[i-1].id
        #     statements[i].next_id = statements[i+1].id
        # statements[len(statements)-1].previous_id = statements[len(statements)-2].id
        # return statements
    def preprocessed(self,conversation,**kwargs):
        """
        type_of: string 
            type of conversation : CHAT QA COMMAND MISSION
        persona: string
            *[all] botName[指定bot] userName[指定user]
        [[],[],...]
        preproces data to statements[Statement]
        """
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
                ans_statement.previous_id = input_statement.id
                statements_to_create.append(ans_statement)
            print_progress_bar(
                'QA Trainer',
                index + 1, len(conversation)
            )
        return statements_to_create
