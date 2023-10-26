from ..adapters import Adapter


class AbstractSearch(Adapter):
    name = "Abstract Search"
    def __init__(self,matchsys,**kwargs):
        self.matchsys = matchsys
        # 对话CHAT类型上下文长度 5 句，问答类型QA 只有多个回答，任务TASK类型追溯整个对话
        self.history_length = kwargs.get('history_length', 5)
    
    def search(self,input_statement, **additional_parameters):
        pass