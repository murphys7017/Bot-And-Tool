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
        Train the chat bot based on the provided list of
        statements that represents a single conversation.
        """

        source = kwargs.get('source', 'TRAIN_DATA')


        # 上一个语句文本
        previous_statement_text = None
        # 上一条语句搜索文本
        previous_statement_search_text = ''

        statements_to_create = []


        for conversation_count, conversation in enumerate(conversations):
            if self.show_training_progress:
                print_progress_bar(
                    'Chat List Trainer',
                    conversation_count + 1, len(conversations)
                )
            previous_snowkey = None
            snowkey = self.chatbot.snowkey.get_id()
            next_snowkey = self.chatbot.snowkey.get_id()
            for text in conversation:
                statement_search_text = self.chatbot.storage.tagger.get_text_index_string(text)
                
                statement = self.get_preprocessed_statement(
                    Statement(
                        snowkey=snowkey,
                        text=text,
                        search_text=statement_search_text,
                        next_snowkey=next_snowkey,
                        previous_snowkey=previous_snowkey,
                        conversation='TRAIN_DATA',
                        type_of='CHAT',
                        source=source,
                    )
                )
                previous_snowkey = snowkey
                snowkey = next_snowkey
                next_snowkey = self.chatbot.snowkey.get_id()

                statements_to_create.append(statement)
        
        self.chatbot.storage.create_many(statements_to_create)
        self.chatbot.docvector_tool.train(statements_to_create)
