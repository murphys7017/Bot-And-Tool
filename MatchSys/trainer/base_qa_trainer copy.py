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
        
        temp_conversation_key_index = {}
        temp_conversation_values = []
        index_count = 0
        for key,value in conversation.items():
            index_count = len(value) + index_count
            temp_conversation_key_index[key] = index_count
            for i in value:
                temp_conversation_values.append(i)
        
        source = kwargs.get('source', 'TRAIN_DATA')
        conversation_text = kwargs.get('conversation', 'TRAIN_DATA')
        previous_id = 0
        next_id = 0
        kwargs['type_of'] = 'Q'
        kwargs['persona'] = 'user:*'
        input_statements = message_adapter.process_list(list(conversation.keys()),**kwargs)

        kwargs['type_of'] = 'A'
        kwargs['persona'] = 'bot:'+self.matchsys.name
        ans_statements = message_adapter.process_list(temp_conversation_values)
        previous_statement_len = 0
        for input_statement in input_statements:
            statements_to_create.append(input_statement)
            next_statement_len = temp_conversation_key_index[input_statement.text]
            for ans_statement in ans_statements[previous_statement_len:next_statement_len]:
                ans_statement.previous_id = input_statement.previous_id
                statements_to_create.append(ans_statement)

            
        # # TODO: 优化 同样对回复进行处理，一个问答一个问答分批处理太浪费时间
        # for index,input_statement in enumerate(input_statements):
        #         print_progress_bar(
        #             'QA Trainer',
        #             index + 1, len(conversation)
        #         )
        #         statements_to_create.append(input_statement)
        #         kwargs['previous_id'] = input_statement.id
        #         kwargs['type_of'] = 'A'
        #         kwargs['persona'] = 'bot:'+self.matchsys.name
        #         if input_statement.text in conversation:
        #             try:
        #                 for statement in  message_adapter.process_list(conversation[input_statement.text],**kwargs):
        #                     statements_to_create.append(statement)
        #             except Exception as e:
        #                 print(input_statement.text)
        #                 print(conversation[input_statement.text])
        #         else:
        #             print(input_statement)
        self.matchsys.storage.create_many(statements_to_create)
        self.matchsys.docvector_tool.train(statements_to_create)