from ..comparisons import LevenshteinDistance
from .logic_adapter import LogicAdapter

class BestMatch(LogicAdapter):
    """
    TODO:将从search获取到的几个可能的对话进行比对，返回最有可能的一个
    A logic adapter that returns a response based on known responses to
    the closest matches to the input statement.

    :param excluded_words:
        The excluded_words parameter allows a list of words to be set that will
        prevent the logic adapter from returning statements that have text
        containing any of those words. This can be useful for preventing your
        chat bot from saying swears when it is being demonstrated in front of
        an audience.
        Defaults to None
    :type excluded_words: list
    """

    def __init__(self, matchsys, **kwargs):
        super().__init__(matchsys, **kwargs)
        self.statement_comparison = kwargs.get(
            'statement_comparison_function',
            LevenshteinDistance()
        )

        self.frequency_match_statements = kwargs.get('frequency_match_statements', 1)
        self.min_confidence = kwargs.get('min_confidence',0.9)
        self.excluded_words = kwargs.get('excluded_words')
    
    def compare_history(self, statement):
        similarity_rate = 0
        for db_statement, history_statement in zip(statement.history_statements, self.matchsys.history):
            similarity_rate += self.statement_comparison_function(db_statement, history_statement)
        return similarity_rate

    def default_responses_process(self, statement):
        return None

    def process(self, search_results):
        response_list = []
        # Search for the closest match to the input statement
        for result in search_results:
            if self.compare_history(result) >= self.min_confidence:
                response_list.append(result)

        if len(response_list)>0:
          
            results = []
            same_result_mark = {}
            for result in response_list:
                if result.id in same_result_mark:
                    same_result_mark[result.id]['count'] += 1
                else:
                    same_result_mark[result.id] = {'count':1,'result':result}
                
            for key,value in same_result_mark.items():
                if value['count'] > self.frequency_match_statements:
                    results.append(same_result_mark[key]['result'])
            if len(results) > 0:
                response = results[0]
                for result in results:
                    if response.mark < result.mark:
                        response = result
                return response
        
        return self.default_responses_process('')