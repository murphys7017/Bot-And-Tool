"""
Match Core
"""
class Doc2VecTool(object):
    model = None
    TaggedDocument = None
    def __init__(self, **kwargs):
        """
        vector_similarity_ratex 相似率大于这个值才会添加到返回集中
        most_similar_number 一次匹配取多少个结果
        vector_match_times 匹配几次
        vector_similarity_rate_diff 相似率差别大于vector_similarity_rate_diff的才会添加到结果集
        """
        import os
        from MatchSys import config
        from gensim.models import Doc2Vec
        from gensim.models.doc2vec import TaggedDocument
        
        self.vector_similarity_rate = kwargs.get('vector_similarity_rate',config.VECTOR_SIMILARITY_RATE)
        self.most_similar_number = kwargs.get('most_similar_number',config.VECTOR_SIMILAR_NUMBER)
        self.vector_match_times = kwargs.get('vector_match_times',config.VECTOR_MMATCH_TIMES)
        self.vector_similarity_rate_diff = kwargs.get('vector_similarity_rate_diff', config.VECTOR_SIMILARITY_RATE_DIFF)

        self.text_vec_model_path = kwargs.get('text_vec_model_path', config.VECTOR_MODEL_PATH)

        if os.path.exists(self.text_vec_model_path):
            self.model = Doc2Vec.load(os.path.abspath(self.text_vec_model_path))

    def remove_stopwords(self,words):
        import jieba
        return jieba.lcut_for_search(words)
        # return words
    def train(self,statements):
        import time
        start = time.perf_counter()
        if self.model is not None:
            print("updating model")
            self.update_model(statements)
            
        else:
            print("training model")
            self.train_model(statements)
        self.save_model(self.text_vec_model_path+"new_model")
        end = time.perf_counter()
        print("运行时间：", end - start, "秒")

    def build_tokenzied(self,statements):
        from gensim.models.doc2vec import TaggedDocument
        tokenized = []
        for statement in statements:
            if statement.previous_id is None or statement.previous_id == '' or statement.previous_id == 0:
                tokenized.append(TaggedDocument(statement.search_text.split(' '),tags=[str(statement.id)]))
        return tokenized
    
    def train_model(self, statements):
        from gensim.models import Doc2Vec

        tokenized = self.build_tokenzied(statements)

        self.model = Doc2Vec(tokenized,dm=1, window=8, min_count=1, workers=4)
        self.model.train(tokenized,total_examples=self.model.corpus_count,epochs=100)
        
    
    def save_model(self,save_path):
        import os
        self.model.save(os.path.abspath(save_path))
        
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
    
    def update_model(self,statements):
        tokenized = self.build_tokenzied(statements)

        if len(tokenized) > 0:
            self.model.build_vocab(tokenized,update=True) #注意update = True 这个参数很重要
            self.model.train(tokenized,total_examples=self.model.corpus_count,epochs=100)