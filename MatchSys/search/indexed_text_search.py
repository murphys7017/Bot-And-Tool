from MatchSys.search.search_adapter import SearchAdapter
from MatchSys.utils import get_time


class IndexedTextSearch(SearchAdapter):
    """
    :param statement_comparison_function: A comparison class.
        Defaults to ``LevenshteinDistance``.

    :param search_page_size:
        The maximum number of records to load into memory at a time when searching.
        Defaults to 1000
    """

    name = 'indexed_text_search'

    def __init__(self, matchsys, **kwargs):
        SearchAdapter.__init__(self, matchsys, **kwargs)
        from MatchSys.comparisons import LevenshteinDistance


        statement_comparison_function = kwargs.get(
            'statement_comparison_function',
            LevenshteinDistance
        )

        self.compare_statements = statement_comparison_function()

        self.search_page_size = kwargs.get(
            'search_page_size', 1000
        )

    def search(self, input_statement):
        """
        Search for close matches to the input. Confidence scores for
        subsequent results will order of increasing value.

        :param input_statement: A statement.
        :type input_statement: chatterbot.conversation.Statement

        :param **additional_parameters: Additional parameters to be passed
            to the ``filter`` method of the storage adapter when searching.

        :rtype: Generator yielding one closest matching statement at a time.
        """
        self.matchsys.logger.info('Beginning search for close text match')

        input_search_text = input_statement.search_text

        if not input_statement.search_text:
            self.matchsys.logger.warn(
                'No value for search_text was available on the provided input'
            )


        search_parameters = {
            'search_text_contains': input_search_text,
            'persona_not_startswith': 'bot:',
            'page_size': self.search_page_size
        }

        statement_list = self.matchsys.storage.filter(**search_parameters)

        best_confidence_so_far = 0

        self.matchsys.logger.info('Processing search results')

        # Find the closest matching known statement
        for statement in statement_list:
            confidence = self.compare_statements(input_statement, statement)

            if confidence > best_confidence_so_far:
                best_confidence_so_far = confidence
                statement.confidence = confidence

                self.matchsys.logger.info('Similar text found: {} {}'.format(
                    statement.text, confidence
                ))

                yield statement