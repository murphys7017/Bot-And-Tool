from MatchSys.utils import get_time
from ..adapters import Adapter


class SearchAdapter(Adapter):
    name = "Abstract Search"
    need_train = False
    history_length = 5
    matchsys = None
    def __init__(self,matchsys,**kwargs):
        self.matchsys = matchsys
        # 对话CHAT类型上下文长度 5 句，问答类型QA 只有多个回答，任务TASK类型追溯整个对话
        self.history_length = kwargs.get('history_length', 5)
    def train(self,):
        pass
    def search(self,input_statement):
        pass
    @get_time
    def build_statement_chain(self, statements):
        all_result = []

        for statement in statements:
            chat_chain = [statement]
            next_statement = statement
            per_statement = statement
            while chat_chain[0].next_id:
                chat_chain.insert(0, self.matchsys.storage.get_statement_by_id(chat_chain[0].next_id))
            while chat_chain[-1].previous_id:
                chat_chain.append(self.matchsys.storage.get_statement_by_id(chat_chain[-1].previous_id))
            # for i in range(self.history_length):
            #     if per_statement.previous_id:
            #         per_statement = self.matchsys.storage.get_statement_by_id(per_statement.previous_id)
            #         statement.history_statements.append(per_statement)
            #     # per_statement = self.matchsys.storage.model_to_object(per_statement)
            #     if next_statement.next_id:
            #         next_statement = self.matchsys.storage.get_statement_by_id(next_statement.next_id)
            #         statement.predict_statements.append(next_statement)
            #     # next_statement = self.matchsys.storage.model_to_object(next_statement)
                    
            print(chat_chain)
            all_result.append(chat_chain)
        return all_result