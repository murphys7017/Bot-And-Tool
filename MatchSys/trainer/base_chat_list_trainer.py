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
    def build_line_relations(self, statements):
        statements[0].next_id = statements[1].id
        for i in range(1,len(statements)-1):
            statements[i].previous_id = statements[i-1].id
            statements[i].next_id = statements[i+1].id
        statements[len(statements)-1].previous_id = statements[len(statements)-2].id
        return statements
