from ..adapters import Adapter
from ..storage import StorageAdapter
from ..search import IndexedTextSearch,DocVectorSearch
from ..object_definition import Statement


class LogicAdapter(Adapter):
    """
    This is an abstract class that represents the interface
    that all logic adapters should implement.

    :param search_algorithm_name: The name of the search algorithm that should
        be used to search for close matches to the provided input.
        Defaults to the value of ``Search.name``.

    :param maximum_similarity_threshold:
        The maximum amount of similarity between two statement that is required
        before the search process is halted. The search for a matching statement
        will continue until a statement with a greater than or equal similarity
        is found or the search set is exhausted.
        Defaults to 0.95

    :param response_selection_method:
          The a response selection method.
          Defaults to ``get_first_response``
    :type response_selection_method: collections.abc.Callable

    :param default_response:
          The default response returned by this logic adaper
          if there is no other possible response to return.
    :type default_response: str or list or tuple
    """

    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)
        from service.MatchSys.utils import get_first_response

        self.search_algorithm_name = kwargs.get(
            'search_algorithm_name',
            DocVectorSearch.name
        )

        self.search_algorithm = self.chatbot.search_algorithms[
            self.search_algorithm_name
        ]
        self.min_confidence = kwargs.get('min_confidence',0.95)

        # By default, select the first available response
        self.select_response = kwargs.get(
            'response_selection_method',
            get_first_response
        )

        default_responses = kwargs.get('default_response', [])

        # Convert a single string into a list
        if isinstance(default_responses, str):
            default_responses = [
                default_responses
            ]

        self.default_responses = [
            Statement(text=default) for default in default_responses
        ]

    def can_process(self, statement):
        """
        A preliminary check that is called to determine if a
        logic adapter can process a given statement. By default,
        this method returns true but it can be overridden in
        child classes as needed.

        :rtype: bool
        """
        return True

    def process(self, statement, additional_response_selection_parameters=None):
        """
        覆盖此方法并实现选择输入语句响应的逻辑。
        应该返回置信度值和所选的响应语句。
        置信度值表示逻辑适配器的准确度
        期望选择的响应为。置信度分数用于选择
        来自多个逻辑适配器的最佳响应。

        置信值应该是介于0和1之间的数字，其中0是
        最低的置信水平，1是最高的。

        参数语句:逻辑适配器要处理的输入语句。
        :type statement:语句

        :param additional_response_selection_parameters:配置时使用的参数
        筛选结果以从中选择响应。
        addtional_response_selection_parameters: dict

        : rtype:声明
        """
        raise self.AdapterMethodNotImplementedError()

    def get_default_response(self, input_statement):
        """
        This method is called when a logic adapter is unable to generate any
        other meaningful response.
        """
        return Statement(text='NO_MATCH_PASS')

    @property
    def class_name(self):
        """
        Return the name of the current logic adapter class.
        This is typically used for logging and debugging.
        """
        return str(self.__class__.__name__)
