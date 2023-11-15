from MatchSys.utils import get_time
from .search_adapter import SearchAdapter


class TextSearch(SearchAdapter):
    """
    """

    name = 'text_search'

    def __init__(self, matchsys, **kwargs):
        self.matchsys = matchsys

    @get_time
    def search(self, input_statement):
        self.matchsys.logger.info('Beginning search for text_search')
        # TODO: inferred2string返回的是id和text 修改为根据id找到对应的statement
        input_statement_list = []
        for statement in self.matchsys.storage.get_statements_by_text(input_statement.text):
            # statement = self.matchsys.storage.model_to_object(statement)
            input_statement_list.append(statement)

        self.matchsys.logger.info('Processing search results')

        return self.build_statement_chain(input_statement_list)


