import random
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
        self.min_confidence = kwargs.get('min_confidence',0.7)
        self.excluded_words = kwargs.get('excluded_words')
    
    def compare_history(self, per_chain):
        similarity_rate = 0
        for db_statement, history_statement in zip(per_chain, self.matchsys.chat_history):
            similarity_rate += self.statement_comparison(db_statement, history_statement)
        return similarity_rate

    def process(self, search_results):
        response = None
        similarity_rate = 0
        for statements in search_results:
            if isinstance(statements,list):
                per_chain = statements[0:1]
                statements = statements[1:]
                temp_similarity_rate = self.compare_history(per_chain)
                if temp_similarity_rate > similarity_rate:
                    response = random.choice(statements)
                    similarity_rate = temp_similarity_rate
            else:
                per_chain = statements[1]
                temp_similarity_rate = self.compare_history(per_chain)
                if temp_similarity_rate > similarity_rate:
                    response = statements[0][-1]
                    similarity_rate = temp_similarity_rate
        if similarity_rate < self.min_confidence:
            response.text = '[小于最小置信度]' + response.text
        return similarity_rate, response