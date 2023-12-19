import os
os.environ['KMP_DUPLICATE_LIB_OK']='TRUE'

import logging
from .object_definition import Statement
from .message import MessageAdapter
from .storage import StorageAdapter
from .logic import LogicAdapter
from .search import SearchAdapter
from .utils import Doc2VecTool, get_time,validate_adapter_class,initialize_class,import_module,IdWorker

from ltp import LTP
import difflib
from MatchSys import config

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
    def match(self,input_statement):
        for key in self.commands:
            # 匹配消息的开头
            if input_statement.text.startswith(key) or input_statement.text.endswith(key):
                return True
            
            # 匹配相似度 计划废弃
            elif difflib.SequenceMatcher(lambda x:x in " \t", str(input_statement.text), key).quick_ratio() > self.command_similarity_rate:
                return True
                    
            # 匹配关键词 计划废弃
            elif ',' in key:
                keys = key.split(',')
                if len(set(keys[:-1]).intersection(input_statement.search_text.split(' '))) > keys[-1:]:
                    return True
            elif '，' in key:
                keys = key.split(',')
                if len(set(keys[:-1]).intersection(input_statement.search_text.split(' '))) > keys[-1:]:
                    return True
        return False
    def handle(self, input_statement,matchsys):
        try: 
            res = self.func(input_statement)
        except Exception as e:
            res = str(e)
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
            max_time_between_conversations
        """
        print("Starting initialization of MatchSys")
        config.initialize(**kwargs)
        
        self.chat_history = []
        self.predict_dialogue = []
        self.command_handles = []
        self.name = kwargs.get('name', 'Alice')
        self.max_time_between_conversations = kwargs.get('max_time_between_conversations',30)
        self.history_length = kwargs.get('history_length', 7)
        self.need_ltp = kwargs.get('need_ltp',True)

        ltp_model_path = kwargs.get('ltp_model_path', 'LTP/small')
        message_adapter_names = kwargs.get('message_adapters', ['MatchSys.message.TextMessageAdapter'])
        storage_adapter_name = kwargs.get('storage_adapter', 'MatchSys.storage.SQLStorageAdapter')
        # TODO:完善intent search
        search_adapters_name_list = kwargs.get('search_adapters_name_list', ['MatchSys.search.DocVectorSearch','MatchSys.search.TextSearch','MatchSys.search.IntentTextSearch'])
        logic_adapter_name_list = kwargs.get('logic_adapters', ['MatchSys.logic.BestMatch'])
        if self.need_ltp:
            ltp = LTP(ltp_model_path)
            # 将模型移动到 GPU 上
            import torch
            if torch.cuda.is_available():
                # ltp.cuda()
                ltp.to("cuda")
            kwargs['ltp'] = ltp

        # 初始化消息处理器
        self.message_adapters = {}
        for message_adapter_name in message_adapter_names:
            validate_adapter_class(message_adapter_name, MessageAdapter)
            message_adapter = initialize_class(message_adapter_name, **kwargs)
            self.message_adapters[message_adapter.class_name] = message_adapter

        # 初始化数据存储
        validate_adapter_class(storage_adapter_name, StorageAdapter)
        self.storage = initialize_class(storage_adapter_name, **kwargs)

        self.search_adapters = []
        for adapter in search_adapters_name_list:
            validate_adapter_class(adapter, SearchAdapter)
            search_adapter = initialize_class(adapter, self, **kwargs)
            self.search_adapters.append(search_adapter)

        # primary_search_algorithm = IndexedTextSearch(self, **kwargs)
        # text_search_algorithm = TextSearch(self, **kwargs)
        # vector_search_algorithm = DocVectorSearch(self, **kwargs)
        # self.search_algorithms = {
        #     primary_search_algorithm.name: primary_search_algorithm,
        #     text_search_algorithm.name: text_search_algorithm,
        #     vector_search_algorithm.name: vector_search_algorithm
        # }

        # 初始化处理逻辑
        self.logic_adapters = []
        for adapter in logic_adapter_name_list:
            validate_adapter_class(adapter, LogicAdapter)
            logic_adapter = initialize_class(adapter, self, **kwargs)
            self.logic_adapters.append(logic_adapter)
        
        # TODO: 添加学习器

        # 日志
        self.logger = kwargs.get('logger', logging.getLogger(__name__))
        self.snowflake = IdWorker(1,1,1)
       
        # 文本向量化工具
        self.docvector_tool = Doc2VecTool(**kwargs)
  
        

    def load_functions(self):
        pass
    def message_handler(self, **kwargs):
        def decorate(fn):
            self.command_handles.append(HandleFunction(func=fn, **kwargs))
            return fn
        return decorate 
        
    def handle_function_declaration(self, **kwargs):
        """声明函数为消息处理函数的注解 @handle_function_declaration
        """
        def decorate(fn):
            self.command_handles.append(HandleFunction(func=fn, **kwargs))
            return fn
        return decorate 

    def get_message_adapter(self, message):
        for messageadapter in self.message_adapters.values():
            if messageadapter.check(message):
                return messageadapter
        return None
    
    def get_response(self, message=None, **kwargs):
        
        """
        Return the bot's response based on the input.
        根据输入的statement生成一个response,这一步进行一些数据验证或者对话学习等，对话匹配流程开始之前和结束后的一些工作

        :param statement: An statement object or string.
        :returns: A response to the input.
        :rtype: Statement

        :param additional_response_selection_parameters: 指定匹配逻辑
        :type additional_response_selection_parameters: dict

        :param persist_values_to_response: MatchSys生成的应当保存到response中的值
        :type persist_values_to_response: dict
        """

        
        
        input_statement = None
        response = None
        # 匹配一个合适的消息处理器,请务必区分清每个处理器的判断规则，只会使用最后一个符合的
        message_adapter = self.get_message_adapter(message)
        if message_adapter is None:
            return None
        input_statement = message_adapter.process(message)

        # 将输入添加到历史对话中
        self.chat_history = self.chat_history[:self.history_length*2]
        self.chat_history.insert(0, input_statement)
        # 判断是否为连续对话
        if (input_statement.created_at - self.chat_history[0].created_at).seconds > self.max_time_between_conversations:
            self.chat_history = [input_statement]
        else:
            pass

    
        if input_statement is not None:
            # 判断是否可以直接匹配到某些函数
            for handle in self.command_handles:
                if handle.check_power(input_statement) and handle.match(input_statement):
                    response =  handle.handle(input_statement,self)
                    self.chat_history[0].next_id = response.id
            
            if response is None:
                # 生成响应Statement
                response = self.generate_response(input_statement)


            # if not self.read_only:
                # self.learn_response(input_statement)

                # Save the response generated for the input
                # self.storage.create(**response.serialize())
            # delete
            if response is not None:
                print(response)
                res_text = message_adapter.process_2_output(response)
                if res_text.startswith('FUNCTION:'):
                    function_name = res_text.split(':')[1]
                    for handle in self.command_handles:
                        if handle.function_id == function_name:
                            response =  handle.handle(input_statement,self)
                            self.chat_history[0].next_id = response.id
                            return message_adapter.process_2_output(response)
                return res_text
    
    def generate_response(self, input_statement):
        """
        Return a response based on a given input statement.

        TODO:根据输入的statement生成一个response
        这一步主要完成了将逻辑处理器返回的消息构建成一个真正的消息
        逻辑处理器可能返回调用指定函数等


        :param input_statement: The input statement to be processed.
        """
        
        #search
        search_results = []
        for search_adapter in  self.search_adapters:
            search_results = search_results + search_adapter.search(input_statement)
        search_results=list(set(search_results))
        search_results = self.build_statement_chain(search_results)

        # logical matching
        similarity_rate = 0
        response = None
        for adapter in self.logic_adapters:
            if adapter.can_process(input_statement):
                t_similarity_rate, t_response = adapter.process(search_results)
                if t_similarity_rate > similarity_rate:
                    similarity_rate = t_similarity_rate
                    response = t_response
        return response
    
    def lean_response(self,statement):
        """排除QA型对话和Task型对话，主要学习Chat型对话，具体的触发lean_response函数的规则还没想好
        Args:
            statement (_type_): _description_
        """
        pass
    @get_time
    def build_statement_chain(self, statements):
        all_result = []

        for statement in statements:
            if statement.type_of == 'Q':
                chat_chain = [statement]
                for res in self.storage.get_statements_by_previous_id(statement.id):
                    chat_chain.append(res)
                all_result.append(chat_chain)
            else:
                next_statement = [statement]
                per_statement = [statement]
                while next_statement[0].next_id:
                    next_statement.insert(0, self.storage.get_statement_by_id(next_statement[0].next_id))
                while per_statement[-1].previous_id:
                    per_statement.append(self.storage.get_statement_by_id(per_statement[-1].previous_id))
                all_result.append((per_statement,next_statement))
        return all_result