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
        source = kwargs.get('source', 'TRAIN_DATA')
        conversation_text = kwargs.get('conversation', 'TRAIN_DATA')
        statements_to_create = []
        previous_id = 0
        next_id = 0
        kwargs['type_of'] = 'Q'
        kwargs['persona'] = 'user:*'

         # 匹配一个合适的消息处理器,请务必区分清每个处理器的判断规则，负责只会使用最后一个符合的
        message_adapter = None
        for messageadapter in self.matchsys.message_adapters:
            if messageadapter.check(list(conversation.keys())[0]):
                message_adapter = messageadapter
        input_statements = message_adapter.process_list(list(conversation.keys()),**kwargs)

        for index,input_statement in enumerate(input_statements):
                if self.show_training_progress:
                    print_progress_bar(
                        'QA Trainer',
                        index + 1, len(conversation)
                    )
                statements_to_create.append(input_statement)
                kwargs['previous_id'] = input_statement.id
                kwargs['type_of'] = 'A'
                kwargs['persona'] = 'bot:'+self.matchsys.name
                for statement in  message_adapter.process_list(conversation[input_statement.text],**kwargs):
                    statements_to_create.append(statement)
        self.matchsys.storage.create_many(statements_to_create)
        self.matchsys.docvector_tool.train(statements_to_create)