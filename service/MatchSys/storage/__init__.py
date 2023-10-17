from service.MatchSys.storage.storage_adapter import StorageAdapter
from service.MatchSys.storage.sql_storage import SQLStorageAdapter
from service.MatchSys.object_definition import Semantic,Statement,Tag


"""
数据存储模块，内容主要为StorageAdapter的实现和对数据库表的映射类
"""
__all__ = (
    'StorageAdapter',
    'SQLStorageAdapter',
    'Semantic',
    'Statement',
    'Tag'
)
