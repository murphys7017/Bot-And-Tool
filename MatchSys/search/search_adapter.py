from MatchSys.utils import get_time
from ..adapters import Adapter


class SearchAdapter(Adapter):
    name = "Abstract Search"
    history_length = 5
    matchsys = None
    def __init__(self,matchsys,**kwargs):
        self.matchsys = matchsys
        # 对话CHAT类型上下文长度 5 句，问答类型QA 只有多个回答，任务TASK类型追溯整个对话
        self.history_length = kwargs.get('history_length', 15)

    def search(self,input_statement):
        pass
    @get_time
    def build_statement_chain(self, statements):
        all_result = []

        for statement in statements:
            if statement.type_of == 'Q':
                statement.predict_statements = []
                for result in self.matchsys.storage.get_statements_by_previous_id(statement.id):
                    # result = self.matchsys.storage.model_to_object(result)
                    statement.predict_statements.append(result)
                
            if statement.type_of == 'CHAT':
                next_statement = statement
                per_statement = statement
                for i in range(self.history_length):
                    if per_statement.previous_id:
                        per_statement = self.matchsys.storage.get_statement_by_id(per_statement.previous_id)
                        statement.history_statements.append(per_statement)
                    # per_statement = self.matchsys.storage.model_to_object(per_statement)
                    if next_statement.next_id:
                        next_statement = self.matchsys.storage.get_statement_by_id(next_statement.next_id)
                        statement.predict_statements.append(next_statement)
                    # next_statement = self.matchsys.storage.model_to_object(next_statement)
                    
                    
            if statement.type_of == 'TASK':
                pass
            all_result.append(statement)
        return all_result