from .search_adapter import SearchAdapter


class IntentTextSearch(SearchAdapter):
    """
    """

    name = 'intent_search'

    def __init__(self, matchsys, **kwargs):
        self.matchsys = matchsys
    
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
        predicates = self.matchsys.storage.get_semantics_by_text(input_statement)

    def search(self, input_statement):
        self.matchsys.logger.info('Beginning search for text_search')
        input_statement_semantics = input_statement.semantics
        maybe_semantics_id = []
        for input_statement_semantic in input_statement_semantics:
            input_not_null = input_statement_semantic.get_not_null()
            semantics = self.matchsys.storage.get_semantics_by_text(input_statement_semantic.predicate)
            for semantic in semantics:
                db_not_null = semantic.get_not_null()
                if input_not_null.keys() == db_not_null.keys():
                    maybe_semantics_id.append(semantic.id)
                    print(input_not_null.keys())

                

        return self.build_statement_chain([])


