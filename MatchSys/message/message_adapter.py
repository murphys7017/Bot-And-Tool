from ..object_definition import Statement,Semantic
from ..utils import import_module, IdWorker


class MessageAdapter(object):
    """
    This is an abstract class that represents the interface
    that all message adapters should implement.
    """
    def __init__(self, **kwargs) -> None:
        from MatchSys.object_definition import Statement,Semantic

        self.snowflake = IdWorker(1,1,1)

        # 初始化预处理程序
        # 建议自行实现，可能导致处理后的和预期的不符，如null '' 等
        preprocessors = kwargs.get('preprocessors', [])
        self.preprocessors = []
        for preprocessor in preprocessors:
            self.preprocessors.append(import_module(preprocessor))
        

        self.ltp = kwargs.get('ltp', None)
        if self.ltp is None:
            print('ltp not found')
            from ltp import LTP
            ltp_model_path = kwargs.get('ltp_model_path', 'LTP/small')
            self.ltp = LTP(ltp_model_path)

        user_dictionary = kwargs.get('user_dictionary',[])
        if len(user_dictionary) > 0:
            self.ltp.add_words(words=user_dictionary, freq=2)

    def check(self, message):
        """
        检查消息是否符合处理器要求，返回True or False
        """
        if message is None or message == '':
            return False
        
        return True
    def process_2_output(self, statement):
        import random
        """
        将statement转化为外部需要的形式
        """
        res = None
        if statement.type_of == 'Q':
           
            res = random.choice(statement.predict_statements)
        # TODO: 对话型整体搜索都需要反馈修改
        elif statement.type_of == 'CHAT':

            res = statement.predict_statements[0]
        return res.text

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
        
        text = text.split('.{')
        if len(text) > 1:
            args = text[1][:-1].split(',')
            for arg in args:
                arg = arg.split('=')
                if len(arg) == 2:
                    kwargs[arg[0]] = arg[1]
     
        kwargs['id'] = self.snowflake.get_id()

        kwargs['text'] = text[0]
        # 分词
        result = self.ltp.pipeline(text[0], tasks=["cws","srl"])

        kwargs['search_text'] = ' '.join(result.cws)
        semantics = []
        if len(result.srl) > 0:
            for item in result.srl:
                temp = {}
                temp['id'] = self.snowflake.get_id()
                temp['predicate'] = item['predicate']
                for arg in item['arguments']:
                    temp[arg[0]] = arg[1]
                semantics.append(Semantic(**temp)) 
        kwargs['semantics'] = semantics
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
        kwargs_list = []
        input_texts = []

        for text in text_list:
            for preprocessor in self.preprocessors:
                text = preprocessor(text)

            text = text.split('.{')
            temp = kwargs
            if len(text) > 1:
                args = text[1][:-1].split(',')
                for arg in args:
                    arg = arg.split('=')
                    if len(arg) == 2:
                        temp[arg[0]] = arg[1]
            input_texts.append(text[0])
            kwargs_list.append(temp)
        input_statements = []

        results = self.ltp.pipeline(input_texts, tasks=["cws","srl"])

        for cws,srl,input_text,kwargs_ in  zip(results.cws,results.srl,input_texts,kwargs_list):
            kwargs_['id'] = self.snowflake.get_id()

            kwargs_['text'] = input_text

            kwargs_['search_text'] = ' '.join(cws)

            semantics = []
            if len(srl) > 0:
                t = srl[0]
                for item in srl:
                    temp = {}
                    temp['id'] = self.snowflake.get_id()
                    temp['predicate'] = item['predicate']
                    for arg in item['arguments']:
                        temp[arg[0]] = arg[1]
                    semantics.append(Semantic(**temp))
            kwargs_['semantics'] = semantics
    
            input_statements.append(Statement(**kwargs_))
        return input_statements
        

    @property
    def class_name(self):
        """
        Return the name of the current logic adapter class.
        This is typically used for logging and debugging.
        """
        return str(self.__class__.__name__)
