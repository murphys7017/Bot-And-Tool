from ..object_definition import Statement,Semantic
from ..utils import import_module, IdWorker


class MessageAdapter(object):
    """
    This is an abstract class that represents the interface
    that all message adapters should implement.
    """
    def __init__(self, **kwargs) -> None:
        from service.MatchSys.object_definition import Statement,Semantic

        self.snowflake = IdWorker(1,1,1)

        # 初始化预处理程序
        preprocessors = kwargs.get('preprocessors', ['jionlp.clean_text'])
        self.preprocessors = []
        for preprocessor in preprocessors:
            self.preprocessors.append(import_module(preprocessor))
        

        self.ltp = kwargs.get('ltp', None)
        if self.ltp is None:
            from ltp import LTP
            ltp_model_path = kwargs.get('ltp_model_path', 'LTP/small')
            self.ltp = LTP(ltp_model_path)

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
        """
        检查消息是否符合处理器要求，返回True or False
        """
        if message is None or message == '':
            raise self.ChatBotException(
                'Either a statement object or a "text" keyword '
                'argument is required. Neither was provided.'
            )
        
        return True
    def process_2_output(self, statement):
        """
        将statement转化为外部需要的形式
        """
        return statement.text

    def process(self, message, **kwargs):
        """
        解析消息，并且将其中的文本以及其他参数封装为statement
        """
        # read the message

        # Get Text message
        input_statement = self.text_process(text=message)

        # Add Other Info

        # 获取Statement
        raise self.AdapterMethodNotImplementedError()

    def text_process(self, text,**kwargs):
        import json
        """将对话文本分词封装为statement给process

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
        result = self.ltp.pipeline(text, tasks=["cws","srl"])
        # TODO: 重新编写
        kwargs['search_text'] = ' '.join(result.cws)
        if len(result.srl) > 0:
            t = result.srl[0]
            for item in result.srl:
                if len(t['arguments']) > len(item['arguments']):
                    t = item
            kwargs['intent'] = json.dumps(t)

        input_statement = Statement(**kwargs)
        return input_statement
    def text_process_list(self, text_list,**kwargs):
        import json
        """Return Search Text

        Args:
            text (_type_): _description_

        Returns:
            _type_: Statement
        """
        # 清理文本
        # for preprocessor in self.preprocessors:
        #     text = preprocessor(text)
        input_statements = []
        result = self.ltp.pipeline(text_list, tasks=["cws","srl"])
        for cws,srl in  zip(result.cws,result.srl):
            kwargs['id'] = self.snowflake.get_id()

            kwargs['text'] = text_list[result.cws.index(cws)]
            print( kwargs['text'])

            kwargs['search_text'] = ' '.join(cws)
            semantics = []
            # TODO: 重新编写
            if len(srl) > 0:
                t = srl[0]
                for item in srl:
                    item['arguments'].append(('id',self.snowflake.get_id()))
                    semantics.append(Semantic(item)) 
            kwargs['semantics'] = semantics
    
            input_statements.append(Statement(**kwargs))
        return input_statements
        

    @property
    def class_name(self):
        """
        Return the name of the current logic adapter class.
        This is typically used for logging and debugging.
        """
        return str(self.__class__.__name__)
