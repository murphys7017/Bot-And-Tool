from MatchSys.utils import get_time
from .search_adapter import SearchAdapter


class IntentTextSearch(SearchAdapter):
    """
    """

    name = 'intent_search'

    def __init__(self, matchsys, **kwargs):
        SearchAdapter.__init__(self, matchsys, **kwargs)
    
    """
    搜索predicate，从中找出意图相似的
    找到对应statement
    从称呼对照表中确认bot和对应客体
    1.找到相同的predicate
    2.找到对应的statement
    3.根据statement对predicate分类
    4.筛选符合的statement
    5.处理参数
    """
    def get_predicate_list(self,input_statement):
        # predicates = self.matchsys.storage.get_semantics_by_text(input_statement)
        pass
    
    @get_time
    def search(self, input_statement):
        self.matchsys.logger.info('Beginning search for text_search')
        input_statement_semantics = input_statement.semantics
        maybe = []
        for input_statement_semantic in input_statement_semantics:
            input_not_null = input_statement_semantic.get_not_null()
            for semantic in self.matchsys.storage.get_semantics_by_text(input_statement_semantic.predicate):
                db_not_null = semantic.get_not_null()
                if input_not_null.keys() == db_not_null.keys():
                    maybe.append(self.matchsys.storage.model_to_object(semantic.statement[0]))
                    # maybe.append(semantic.statement[0])

        return self.build_statement_chain(maybe)


