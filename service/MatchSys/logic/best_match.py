from service.MatchSys.comparisons import LevenshteinDistance
from service.MatchSys.logic import LogicAdapter
from service.MatchSys import utils
from random import choice

class BestMatch(LogicAdapter):
    """
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

    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)
        self.statement_comparison_function = kwargs.get(
            'statement_comparison_function',
            LevenshteinDistance
        )
        self.min_confidence = kwargs.get('min_confidence',0.9)
        self.excluded_words = kwargs.get('excluded_words')
    
    def compare_history(self, statement, input_statement):
        if statement.type_of == 'Q':
            return self.statement_comparison_function(statement, input_statement)
        if statement.type_of == 'CHAT':
            similarity_rate = 0
            for db_statement, history_statement in zip(statement.history_statements, self.chatbot.history):
                similarity_rate += self.statement_comparison_function(db_statement, history_statement)
            return similarity_rate
        return -1


    def process(self, input_statement):
        
        search_results = self.search_algorithm.search(input_statement)
        response_list = []
        # Search for the closest match to the input statement
        for result in search_results:
            if self.compare_history(result,input_statement) >= self.min_confidence:
                response_list.append(result)
        if len(response_list)>0:
            response = response_list[0]

            for result in response_list:
                if response.mark < result.mark:
                    response = result

            return response

        return self.default_responses(input_statement)