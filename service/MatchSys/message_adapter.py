from service.MatchSys.conversation import Statement
from service.MatchSys.utils import import_module


class MessageAdapter(object):
    """
    This is an abstract class that represents the interface
    that all message adapters should implement.
    """
    def __init__(self, **kwargs) -> None:
        from service.MatchSys.conversation import Statement
        # 初始化预处理程序
        preprocessors = kwargs.get('preprocessors', ['jionlp.clean_text'])
        self.preprocessors = []
        for preprocessor in preprocessors:
            self.preprocessors.append(import_module(preprocessor))
        pass

    def check(self, message):
        if message is None or message == '':
            raise self.ChatBotException(
                'Either a statement object or a "text" keyword '
                'argument is required. Neither was provided.'
            )
        
        return True

    def process(self, message):
        # 获取Statement
        kwargs = {}

        if isinstance(message, str):
            kwargs['text'] = message

        if isinstance(message, dict):
            kwargs.update(message)

        

        if hasattr(message, 'serialize'):
            kwargs.update(**message.serialize())

        tags = kwargs.pop('tags', [])

        text = kwargs.pop('text')

        input_statement = Statement(text=text, **kwargs)

        input_statement.add_tags(*tags)
        pass

    def text_process(self, text):
        """Return Search Text

        Args:
            text (_type_): _description_

        Returns:
            _type_: _description_
        """
        # 清理文本
        for preprocessor in self.preprocessors:
            text = preprocessor(text)

        # 分词
      
        return self.storage.tagger.get_text_index_string(text)

    @property
    def class_name(self):
        """
        Return the name of the current logic adapter class.
        This is typically used for logging and debugging.
        """
        return str(self.__class__.__name__)