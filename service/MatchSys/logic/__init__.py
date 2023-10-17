from service.MatchSys.logic.logic_adapter import LogicAdapter
from service.MatchSys.logic.best_match import BestMatch
"""
此模块主要为对于从数据库中查询出来的所有的可能的对话结果进行选择和比对，返回一个最有可能的结果。
"""
__all__ = (
    'LogicAdapter',
    'BestMatch',
)
