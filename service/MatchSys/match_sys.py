import logging
from service.MatchSys.object_definition import Statement
from service.MatchSys.message_adapter import MessageAdapter
from service.MatchSys.storage import StorageAdapter
from service.MatchSys.logic import LogicAdapter
from service.MatchSys.search import TextSearch, IndexedTextSearch, DocVectorSearch
from service.MatchSys.utils import Doc2VecTool,validate_adapter_class,initialize_class,import_module,IdWorker

from ltp import LTP
from service import config
import difflib
config.initialize()

class HandleFunction(object):
    def __init__(self, func, **kwargs) -> None:
        self.command_similarity_rate = kwargs.get('command_similarity_rate',0.9)
        self.commands = kwargs.get('commands',[])
        self.level = kwargs.get('level',5)
        self.activate_id = kwargs.get('activate_id', [])
        self.function_id = kwargs.get('function_id', func.__name__)
        self.func = func
    def check_power(self,input_statement):
        return True
    def match(self,message):
        for key in self.commands:
            # 匹配消息的开头
            if str(message).startswith(key):
                return True
            
            # 匹配相似度 计划废弃
            elif difflib.SequenceMatcher(lambda x:x in " \t", str(message), key).quick_ratio() > self.command_similarity_rate:
                return True
                    
            # 匹配关键词 计划废弃
            # elif ',' in key:
            #     keys = key.split(',')
            #     if len(set(keys[:-1]).intersection(set(jieba.lcut(message)))) > keys[-1:]:
            #         return True
            # elif '，' in key:
            #     keys = key.split(',')
            #     if len(set(keys[:-1]).intersection(set(jieba.lcut(message)))) > keys[-1:]:
            #         return True
    def handle(self, input_statement,matchsys):
        res = self.func(input_statement)
        if isinstance(res, str):
            response = matchsys.message_adapter.text_process(res)
            response.id = matchsys.snowflake.get_id(),
            response.persona='bot:' + matchsys.name
            response.previous_id = input_statement.id
            return response
        elif isinstance(res, Statement):
            return response
        
class MatchSys(object):
    """
    一个修改自chatterbot的对话匹配系统
    """
    def __init__(self, name, **kwargs):
        """
        **kwargs:
            message_adapter:
                ltp_model_path
                user_dictionary
            doc2vce:
                text_vec_model_path
                parrot_similarity_rate
            storage_adapter
            logic_adapters
            preprocessors
        """
   
        self.name = name
        self.snowflake = IdWorker(1,1,1)
        self.max_time_between_conversations = kwargs.get('max_time_between_conversations',30)

        # ltp tool
        ltp_model_path = kwargs.get('ltp_model_path', 'LTP/small')
        kwargs['ltp'] = LTP(ltp_model_path)

        # 初始化预处理程序
        # preprocessors = kwargs.get('preprocessors', ['jionlp.clean_text'])
        # self.preprocessors = []
        # for preprocessor in preprocessors:
        #     self.preprocessors.append(import_module(preprocessor))


        # 初始化消息处理器
        message_adapter_name = kwargs.get('message_adapter', 'service.MatchSys.message_adapter.TextMessageAdapter')
        validate_adapter_class(message_adapter_name, MessageAdapter)
        self.message_adapter = initialize_class(message_adapter_name, **kwargs)

        # 初始化数据存储
        storage_adapter_name = kwargs.get('storage_adapter', 'service.MatchSys.storage.SQLStorageAdapter')
        validate_adapter_class(storage_adapter_name, StorageAdapter)
        self.storage = initialize_class(storage_adapter_name, **kwargs)

        # 初始化匹配逻辑
        primary_search_algorithm = IndexedTextSearch(self, **kwargs)
        text_search_algorithm = TextSearch(self, **kwargs)
        vector_search_algorithm = DocVectorSearch(self, **kwargs)
        self.search_algorithms = {
            primary_search_algorithm.name: primary_search_algorithm,
            text_search_algorithm.name: text_search_algorithm,
            vector_search_algorithm.name: vector_search_algorithm
        }

        # 初始化处理逻辑
        logic_adapter_name_list = kwargs.get('logic_adapters', ['service.MatchSys.logic.BestMatch'])
        self.logic_adapters = []
        for adapter in logic_adapter_name_list:
            validate_adapter_class(adapter, LogicAdapter)
            logic_adapter = initialize_class(adapter, self, **kwargs)
            self.logic_adapters.append(logic_adapter)
        

        # 日志
        self.logger = kwargs.get('logger', logging.getLogger(__name__))

        # 是否自动从对话中学习
        self.read_only = kwargs.get('read_only', False)

        # 文本向量化工具
        self.docvector_tool = Doc2VecTool(**kwargs)

  
        self.history = []

        self.predict_dialogue = []
        self.command_handles = []

       
        
    def handle_function_declaration(self, **kwargs):
        """声明函数为消息处理函数的注解 @handle_function_declaration
        """
        def decorate(fn):
            self.command_handles.append(HandleFunction(func=fn, **kwargs))
            return fn
        return decorate 

    
    def get_response(self, message=None, **kwargs):
        """
        Return the bot's response based on the input.
        TODO:根据输入的statement生成一个response,这一步进行一些数据验证或者对话学习等，对话匹配流程开始之前和结束后的一些工作

        :param statement: An statement object or string.
        :returns: A response to the input.
        :rtype: Statement

        :param additional_response_selection_parameters: 指定匹配逻辑
        :type additional_response_selection_parameters: dict

        :param persist_values_to_response: MatchSys生成的应当保存到response中的值
        :type persist_values_to_response: dict
        """
        if self.message_adapter.check(message):
            input_statement = self.message_adapter.process(message)
      

            additional_response_selection_parameters = kwargs.pop('additional_response_selection_parameters', {})
            persist_values_to_response = kwargs.pop('persist_values_to_response', {})
            # 生成响应Statement
            response = self.generate_response(input_statement, additional_response_selection_parameters)


        # if not self.read_only:
            # self.learn_response(input_statement)

            # Save the response generated for the input
            # self.storage.create(**response.serialize())

        return response
    
    def generate_response(self, input_statement, additional_response_selection_parameters=None):
        """
        Return a response based on a given input statement.

        TODO:根据输入的statement生成一个response
        这一步主要完成了将逻辑处理器返回的消息构建成一个真正的消息
        逻辑处理器可能返回调用指定函数等


        :param input_statement: The input statement to be processed.
        """
        # 将输入添加到历史对话中
        self.history = self.history[:15]
        if len(self.history) > 0:
            if (input_statement.created_at - self.history[0].created_at).seconds > self.max_time_between_conversations:
                self.history.insert(0,input_statement)
            else:
                input_statement.previous_id = self.history[0].id
                self.history.insert(0,input_statement)
        
        response_statement = None

        # 判断是否可以直接匹配到某些函数
        for handle in self.command_handles:
            if handle.check_power(input_statement) and handle.match(input_statement.text):
                response_statement =  handle.handle(input_statement,self)
                self.history[0].next_id = response_statement.id
                return response_statement
        
        # 调用Search获取response
        Statement = self.storage.get_object('statement')

        results = []
        result = None
        max_confidence = -1
        # 获取所有的响应statement
        for adapter in self.logic_adapters:
            # 检查是否符合处理器要求
            if adapter.can_process(input_statement):
                
                result = adapter.process(input_statement)
                result.persona='bot:' + self.name
                results.append(result)

                self.logger.info(
                    '{} selected "{}" as a response with a confidence of {}'.format(
                        adapter.class_name, result.text, result.confidence
                    )
                )
            else:
                self.logger.info(
                    'Not processing the statement using {}'.format(adapter.class_name)
                )

        return results
    
    def lean_response(self,statement):
        pass