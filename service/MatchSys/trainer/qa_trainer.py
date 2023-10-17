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
        input_statements = self.matchsys.message_adapter.process_list(list(conversation.keys()),**kwargs)
        for index,input_statement in enumerate(input_statements):
                if self.show_training_progress:
                    print_progress_bar(
                        'QA Trainer',
                        index + 1, len(conversation)
                    )
                try:
                    statements_to_create.append(input_statement)
                    kwargs['id'] = next_id
                    kwargs['type_of'] = 'A'
                    kwargs['persona'] = 'bot:'+self.matchsys.name
                    for statement in  self.matchsys.message_adapter.process_list(conversation[input_statement.text],**kwargs):

                        statements_to_create.append(statement)
                except Exception as e:
                    print(statement)
        self.matchsys.storage.create_many(statements_to_create)
        self.matchsys.docvector_tool.train(statements_to_create)