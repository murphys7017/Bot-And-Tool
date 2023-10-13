from service.MatchSys.conversation import Statement
from service.MatchSys.utils_bk import IdWorker
from service.MatchSys.utils import import_module


class MessageAdapter(object):
    """
    This is an abstract class that represents the interface
    that all message adapters should implement.
    """
    def __init__(self, **kwargs) -> None:
        from service.MatchSys.conversation import Statement
        from ltp import LTP
        self.snowflake = IdWorker(1,1,1)

        # 初始化预处理程序
        preprocessors = kwargs.get('preprocessors', ['jionlp.clean_text'])
        self.preprocessors = []
        for preprocessor in preprocessors:
            self.preprocessors.append(import_module(preprocessor))
        
        model_path = kwargs.get('model_path', 'LTP/small')
        self.ltp = LTP(model_path)

        user_dictionary = kwargs.get('user_dictionary',[])
        if len(user_dictionary) > 0:
            self.ltp.add_words(words=user_dictionary, freq=2)
    class AdapterMethodNotImplementedError(NotImplementedError):
        """
        An exception to be raised when an adapter method has not been implemented.
        Typically this indicates that the developer is expected to implement the
        method in a subclass.
        """

        def __init__(self, message='This method must be overridden in a subclass method.'):
            """
            Set the message for the exception.
            """
            super().__init__(message)

    def check(self, message):
        if message is None or message == '':
            raise self.ChatBotException(
                'Either a statement object or a "text" keyword '
                'argument is required. Neither was provided.'
            )
        
        return True

    def process(self, message, **kwargs):
        # read the message

        # Get Text message
        input_statement = self.text_process(text=message)

        # Add Other Info

        # 获取Statement
        raise self.AdapterMethodNotImplementedError()

    def text_process(self, text,**kwargs):
        """Return Search Text

        Args:
            text (_type_): _description_

        Returns:
            _type_: Statement
        """
        # 清理文本
        for preprocessor in self.preprocessors:
            text = preprocessor(text)
        
        kwargs['id'] = self.snowflake.get_id()

        kwargs['text'] = text
        # 分词
        result = self.ltp.pipeline('你觉得A怎么样', tasks = ["cws","srl"])
        kwargs['search_text'] = ' '.join(result.cws)

        t = result.srl[0]
        for item in result.srl:
            if len(t['arguments']) > len(item['arguments']):
                t = item
        kwargs['intent'] = t


        input_statement = Statement(**kwargs)
        return input_statement

    @property
    def class_name(self):
        """
        Return the name of the current logic adapter class.
        This is typically used for logging and debugging.
        """
        return str(self.__class__.__name__)

class TextMessageAdapter(MessageAdapter):
    """
    This is an abstract class that represents the interface
    that all message adapters should implement.
    """
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def process(self, message, **kwargs):
        # read the message

        # Get Text message
        input_statement = self.text_process(text=message,**kwargs)

        # Add Other Info

        # 获取Statement
        return input_statement