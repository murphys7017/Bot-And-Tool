import os
from MatchSys.utils import get_time
from .search_adapter import SearchAdapter

class DocVectorSearch(SearchAdapter):
    name = 'doc_vector_search'
    model = None
    need_train = True
    TaggedDocument = None

    def __init__(self, matchsys, **kwargs):
        SearchAdapter.__init__(self, matchsys, **kwargs)
        import os
        from MatchSys import config
        from gensim.models import Doc2Vec
        
        self.vector_similarity_rate = kwargs.get('vector_similarity_rate',config.VECTOR_SIMILARITY_RATE)
        self.most_similar_number = kwargs.get('most_similar_number',config.VECTOR_SIMILAR_NUMBER)
        self.vector_match_times = kwargs.get('vector_match_times',config.VECTOR_MMATCH_TIMES)
        self.vector_similarity_rate_diff = kwargs.get('vector_similarity_rate_diff', config.VECTOR_SIMILARITY_RATE_DIFF)

        self.text_vec_model_path = kwargs.get('text_vec_model_path', config.VECTOR_MODEL_PATH)

        if os.path.exists(self.text_vec_model_path):
            self.model = Doc2Vec.load(os.path.abspath(self.text_vec_model_path))

        # self.matchsys = matchsys
        
        # # 对话CHAT类型上下文长度 5 句，问答类型QA 只有多个回答，任务TASK类型追溯整个对话
        # self.history_length = kwargs.get('history_length', 15)

    @get_time
    def search(self, input_statement):
        """
        TODO:完事流程
        先从数据库中找出相似的输入语句，在根据输入语句从数据库中查询出对应的对话，再根据相似度返回对话列表
        """
        self.matchsys.logger.info('Beginning search for doc_vector_search')
        # TODO: inferred2string返回的是id和text 修改为根据id找到对应的statement
        input_statement_list = []
        print('Search List:'+input_statement.search_text) 
        for input_statement_id in self.inferred2string(input_statement.search_text.split(' ')):
            statement = self.matchsys.storage.get_statement_by_id(int(input_statement_id))
            # statement = self.matchsys.storage.model_to_object(statement)
            input_statement_list.append(statement)
        print('DocVectorSearch Match {} result'.format(len(input_statement_list)))
        self.matchsys.logger.info('Processing search results')

        return self.build_statement_chain(input_statement_list)



    @get_time
    def train(self):
        from gensim.models import Doc2Vec
        from gensim.models.doc2vec import TaggedDocument
        
        tokenized = []
        for statement in self.matchsys.storage.get_all_statements():
            # TODO: 这是什么玩意啊，我为啥要加这个判断
            # 明白了，过滤QA中的A
            if statement.type_of == 'QA':
                if statement.previous_id is None or statement.previous_id == '' or statement.previous_id == 0:
                    tokenized.append(TaggedDocument(statement.search_text.split(' '),tags=[str(statement.id)]))
            else:
                tokenized.append(TaggedDocument(statement.search_text.split(' '),tags=[str(statement.id)]))


        self.model = Doc2Vec(tokenized,dm=1, window=8, min_count=1, workers=4)
        self.model.train(tokenized,total_examples=self.model.corpus_count,epochs=100)
        self.model.save(os.path.abspath(self.text_vec_model_path))
        
    def inferred2string(self,words):
        # TODO: 计划两种匹配模式 1.最相似的n项 2.相似率差别大于vector_similarity_rate_diff的
        self.vector_similarity_rate_diff

        inferred_vector = self.model.infer_vector(doc_words=words)
        res = []
        for i in range(self.vector_match_times):
            sims = self.model.dv.most_similar([inferred_vector],topn=self.most_similar_number)
            
            for sim in sims:
                if sim[1] >= self.vector_similarity_rate:
                    res.append(sim[0])
        return res