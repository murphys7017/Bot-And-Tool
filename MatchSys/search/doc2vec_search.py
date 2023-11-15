from MatchSys.utils import get_time
from .search_adapter import SearchAdapter

class DocVectorSearch(SearchAdapter):
    name = 'doc_vector_search'

    def __init__(self, matchsys, **kwargs):
        SearchAdapter.__init__(self, matchsys, **kwargs)

        # self.matchsys = matchsys
        
        # # 对话CHAT类型上下文长度 5 句，问答类型QA 只有多个回答，任务TASK类型追溯整个对话
        # self.history_length = kwargs.get('history_length', 15)

    @get_time
    def search(self, input_statement):
        """
        TODO:完事流程
        先从数据库中找出相似的输入语句，在根据输入语句从数据库中查询出对应的对话，再根据相似度返回对话列表
        """
        self.matchsys.logger.info('Beginning search for doc_vector_search')
        # TODO: inferred2string返回的是id和text 修改为根据id找到对应的statement
        input_statement_list = []
        print('Search List:'+input_statement.search_text) 
        for input_statement_id in self.matchsys.docvector_tool.inferred2string(input_statement.search_text.split(' ')):
            statement = self.matchsys.storage.get_statement_by_id(int(input_statement_id))
            # statement = self.matchsys.storage.model_to_object(statement)
            input_statement_list.append(statement)
        print('DocVectorSearch Match {} result'.format(len(input_statement_list)))
        self.matchsys.logger.info('Processing search results')

        return self.build_statement_chain(input_statement_list)