from .search_adapter import AbstractSearch
from .doc2vec_search import DocVectorSearch
from .indexed_text_search import IndexedTextSearch
from .text_search import TextSearch
"""
此模块主要负责的是根据输入的statement去数据中查找相似的statement并返回包含的整个对话
"""
__all__ = (
    'AbstractSearch',
    'DocVectorSearch',
    'IndexedTextSearch',
    'TextSearch'
)