from .trainer import Trainer
from ..object_definition import Statement
from ..utils import print_progress_bar
class ChatListTrainer(Trainer):
    """
    [[...][...][...]...]
    Allows a chat bot to be trained using a list of strings
    where the list represents a conversation.
    """

    def train(self, conversations,**kwargs):
        """
        [
        xxx
        xxx
        xxx
        xxx
        END
        xxx
        xxx
        xxx.{指定参数，响应角色，权限等参数}
        END
        ]
        Train the chat bot based on the provided list of
        statements that represents a single conversation.
        """
        

        kwargs['source'] = 'TRAIN_DATA'
    
        statements_to_create = []
        message_adapter = self.matchsys.get_message_adapter('默认使用')
        print('start process to statement need long time')
        statements = message_adapter.process_list(conversations, **kwargs)

        per_statement_id = None

        for i in range(len(statements)):
            statement = statements[i]
            if statement.text == 'END':
                per_statement_id = None
  
            else:
                if statements[i+1].text != 'END':
                    statement.next_id = statements[i+1].id
                statement.previous_id = per_statement_id
                per_statement_id = statement.id
            
                statements_to_create.append(statement)


            
        
        self.matchsys.storage.create_many(statements_to_create)
        self.matchsys.docvector_tool.train(statements_to_create)
