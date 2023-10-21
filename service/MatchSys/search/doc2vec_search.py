from .search_adapter import AbstractSearch

class DocVectorSearch(AbstractSearch):
    name = 'doc_vector_search'

    def __init__(self, matchsys, **kwargs):
        from service.MatchSys.comparisons import LevenshteinDistance

        self.matchsys = matchsys
        
        # 对话CHAT类型上下文长度 5 句，问答类型QA 只有多个回答，任务TASK类型追溯整个对话
        self.history_length = kwargs.get('history_length', 5)

    def search(self, input_statement, **additional_parameters):
        """
        TODO:完事流程
        先从数据库中找出相似的输入语句，在根据输入语句从数据库中查询出对应的对话，再根据相似度返回对话列表
        """
        self.matchsys.logger.info('Beginning search for doc_vector_search')
        # TODO: inferred2string返回的是id和text 修改为根据id找到对应的statement
        input_statement_list = []
        for input_statement_id in self.matchsys.docvector_tool.inferred2string(input_statement.search_text.split(' ')):
            statement = self.matchsys.storage.get_statement_by_id(int(input_statement_id))
            statement = self.matchsys.storage.model_to_object(statement)
            input_statement_list.append(statement)

        self.matchsys.logger.info('Processing search results')

        all_result = []

        # Find the closest matching known statement
        for statement in input_statement_list:
            
            if statement.type_of == 'Q':
                results =  self.matchsys.storage.get_statements_by_previous_id(statement.id)
                statement.predict_statements = []
                for result in results:
                    result = self.matchsys.storage.model_to_object(result)
                    statement.predict_statements.append(result)
                
            if statement.type_of == 'CHAT':
                next_statement = statement
                per_statement = statement
                for i in range(self.history_length):
                    per_statement = self.matchsys.storage.get_statement_by_id(per_statement.previous_id)
                    per_statement = self.matchsys.storage.model_to_object(per_statement)
                    next_statement = self.matchsys.storage.get_statement_by_id(next_statement.next_id)
                    next_statement = self.matchsys.storage.model_to_object(next_statement)
                    statement.history_statements.append(per_statement)
                    statement.predict_statements.append(next_statement)
            if statement.type_of == 'TASK':
                pass
            all_result.append(statement)
        return all_result