import os
from service.MatchSys.conversation import Statement
from service.MatchSys import utils


class Trainer(object):
    """
    训练器基类

    :param boolean show_training_progress: Show progress indicators for the
           trainer. The environment variable ``CHATTERBOT_SHOW_TRAINING_PROGRESS``
           can also be set to control this. ``show_training_progress`` will override
           the environment variable if it is set.
    """

    def __init__(self, chatbot, **kwargs):
        self.chatbot = chatbot

        environment_default = os.getenv('CHATTERBOT_SHOW_TRAINING_PROGRESS', True)
        self.show_training_progress = kwargs.get(
            'show_training_progress',
            environment_default
        )

    def get_preprocessed_statement(self, input_statement):
        """
        Preprocess the input statement.
        """
        for preprocessor in self.chatbot.preprocessors:
            input_statement = preprocessor(input_statement)

        return input_statement

    def train(self, *args, **kwargs):
        """
        This method must be overridden by a child class.
        """
        raise self.TrainerInitializationException()

    class TrainerInitializationException(Exception):
        """
        Exception raised when a base class has not overridden
        the required methods on the Trainer base class.
        """

        def __init__(self, message=None):
            default = (
                'A training class must be specified before calling train(). '
                'See http://chatterbot.readthedocs.io/en/stable/training.html'
            )
            super().__init__(message or default)

    def _generate_export_data(self):
        result = []
        for statement in self.chatbot.storage.filter():
            if statement.in_response_to:
                result.append([statement.in_response_to, statement.text])

        return result

    def export_for_training(self, file_path='./export.json'):
        """
        Create a file from the database that can be used to
        train other chat bots.
        """
        import json
        export = {'conversations': self._generate_export_data()}
        with open(file_path, 'w+', encoding='utf8') as jsonfile:
            json.dump(export, jsonfile, ensure_ascii=False)


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
                utils.print_progress_bar(
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
        source = kwargs.get('source', 'TRAIN_DATA')
        conversation_text = kwargs.get('conversation', 'TRAIN_DATA')
        statements_to_create = []
        previous_snowkey = 0
        next_snowkey = 0
        for index,Q in enumerate(conversation):
            if self.show_training_progress:
                utils.print_progress_bar(
                    'QA Trainer',
                    index + 1, len(conversation)
                )
            statement_search_text = self.chatbot.storage.tagger.get_text_index_string(Q)
            snowkey = self.chatbot.snowkey.get_id(),

            statement = self.get_preprocessed_statement(
                                    Statement(
                                        snowkey=snowkey,
                                        text=Q,
                                        search_text=self.chatbot.storage.tagger.get_text_index_string(Q),
                                        previous_snowkey=None,
                                        next_snowkey=-snowkey,
                                        conversation=conversation_text,
                                        type_of='Q',
                                        source=source,
                                        persona='user'
                                    )
                                )
            statements_to_create.append(statement)
            for A in conversation[Q]:
                statement = self.get_preprocessed_statement(
                                    Statement(
                                        snowkey=-snowkey,
                                        text=A,
                                        search_text=self.chatbot.storage.tagger.get_text_index_string(A),
                                        previous_snowkey=snowkey,
                                        next_snowkey=None,
                                        conversation=conversation,
                                        type_of='A',
                                        source=source,
                                        persona='bot:'+self.chatbot.name
                                    )
                                )
                statements_to_create.append(statement)
        self.chatbot.storage.create_many(statements_to_create)
        self.chatbot.docvector_tool.train(statements_to_create)