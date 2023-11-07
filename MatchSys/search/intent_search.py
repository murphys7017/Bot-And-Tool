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
        # TODO: inferred2string返回的是id和text 修改为根据id找到对应的statement
        input_statement_semantics = input_statement.semantics
        for input_statement_semantic in input_statement_semantics:
            semantics = self.matchsys.storage.get_semantics_by_text(input_statement_semantic.predicate)
            print(semantics)

        return self.build_statement_chain([])


