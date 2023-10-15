from random import choice


class IndexedTextSearch:
    """
    :param statement_comparison_function: A comparison class.
        Defaults to ``LevenshteinDistance``.

    :param search_page_size:
        The maximum number of records to load into memory at a time when searching.
        Defaults to 1000
    """

    name = 'indexed_text_search'

    def __init__(self, chatbot, **kwargs):
        from service.MatchSys.comparisons import LevenshteinDistance

        self.chatbot = chatbot

        statement_comparison_function = kwargs.get(
            'statement_comparison_function',
            LevenshteinDistance
        )

        self.compare_statements = statement_comparison_function()

        self.search_page_size = kwargs.get(
            'search_page_size', 1000
        )

    def search(self, input_statement, **additional_parameters):
        """
        Search for close matches to the input. Confidence scores for
        subsequent results will order of increasing value.

        :param input_statement: A statement.
        :type input_statement: chatterbot.conversation.Statement

        :param **additional_parameters: Additional parameters to be passed
            to the ``filter`` method of the storage adapter when searching.

        :rtype: Generator yielding one closest matching statement at a time.
        """
        self.chatbot.logger.info('Beginning search for close text match')

        input_search_text = input_statement.search_text

        if not input_statement.search_text:
            self.chatbot.logger.warn(
                'No value for search_text was available on the provided input'
            )

            input_search_text = self.chatbot.storage.tagger.get_text_index_string(
                input_statement.text
            )

        search_parameters = {
            'search_text_contains': input_search_text,
            'persona_not_startswith': 'bot:',
            'page_size': self.search_page_size
        }

        if additional_parameters:
            search_parameters.update(additional_parameters)

        statement_list = self.chatbot.storage.filter(**search_parameters)

        best_confidence_so_far = 0

        self.chatbot.logger.info('Processing search results')

        # Find the closest matching known statement
        for statement in statement_list:
            confidence = self.compare_statements(input_statement, statement)

            if confidence > best_confidence_so_far:
                best_confidence_so_far = confidence
                statement.confidence = confidence

                self.chatbot.logger.info('Similar text found: {} {}'.format(
                    statement.text, confidence
                ))

                yield statement




class DocVectorSearch:
    name = 'doc_vector_search'

    def __init__(self, chatbot, **kwargs):
        from service.MatchSys.comparisons import LevenshteinDistance

        self.chatbot = chatbot
        
        # 对话CHAT类型上下文长度 5 句，问答类型QA 只有多个回答，任务TASK类型追溯整个对话
        self.history_length = kwargs.get('history_length', 5)

    def search(self, input_statement, **additional_parameters):
        """
        先从数据库中找出相似的输入语句，在根据输入语句从数据库中查询出对应的对话，再根据相似度返回某一对话
        """
        self.chatbot.logger.info('Beginning search for doc_vector_search')

        input_statement_list = self.chatbot.docvector_tool.inferred2string(input_statement.search_text.split(' '))

        self.chatbot.logger.info('Processing search results')

        all_result = []

        # Find the closest matching known statement
        for statement in input_statement_list:
            
            if statement.type_of == 'Q':
                result =  self.chatbot.storage.get_statements_by_id(-statement.id)
                statement.predict_statements = result
                
            if statement.type_of == 'CHAT':
                statement.history_statements.append(statement)
                next_statement = statement
                per_statement = statement
                for i in range(self.history_length):
                    per_statement = self.chatbot.storage.get_statement_by_id(per_statement.previous_id)
                    next_statement = self.chatbot.storage.get_statement_by_id(next_statement.next_id)
                    statement.history_statements.append(per_statement)
                    statement.predict_statements.append(next_statement)
                statement.total_statements = result
            if statement.type_of == 'TASK':
                pass


            # TODO：返回置信度最高的那个
        return all_result




class TextSearch:
    """
    :param statement_comparison_function: A comparison class.
        Defaults to ``LevenshteinDistance``.

    :param search_page_size:
        The maximum number of records to load into memory at a time when searching.
        Defaults to 1000
    """

    name = 'text_search'

    def __init__(self, chatbot, **kwargs):
        from service.MatchSys.comparisons import LevenshteinDistance

        self.chatbot = chatbot

        statement_comparison_function = kwargs.get(
            'statement_comparison_function',
            LevenshteinDistance
        )
        self.compare_statements = statement_comparison_function()


        self.search_page_size = kwargs.get(
            'search_page_size', 1000
        )

    def search(self, input_statement, **additional_parameters):
        """
        Search for close matches to the input. Confidence scores for
        subsequent results will order of increasing value.

        :param input_statement: A statement.
        :type input_statement: chatterbot.conversation.Statement

        :param **additional_parameters: Additional parameters to be passed
            to the ``filter`` method of the storage adapter when searching.

        :rtype: Generator yielding one closest matching statement at a time.
        """
        self.chatbot.logger.info('Beginning search for close text match')

        search_parameters = {
            'persona_not_startswith': 'bot:',
            'page_size': self.search_page_size
        }

        if additional_parameters:
            search_parameters.update(additional_parameters)

        statement_list = self.chatbot.storage.filter(**search_parameters)

        best_confidence_so_far = 0

        self.chatbot.logger.info('Processing search results')

        # Find the closest matching known statement
        for statement in statement_list:
            confidence = self.compare_statements(input_statement, statement)

            if confidence > best_confidence_so_far:
                best_confidence_so_far = confidence
                statement.confidence = confidence

                self.chatbot.logger.info('Similar text found: {} {}'.format(
                    statement.text, confidence
                ))

                yield statement


