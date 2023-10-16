"""
Match Core
"""
class Doc2VecTool(object):
    model = None
  
    def __init__(self,storage, **kwargs):
        import os
        from service import config
        from gensim.models import Doc2Vec

        self.storage = storage
        
        self.parrot_similarity_rate = kwargs.get('parrot_similarity_rate',config.parrot_similarity_rate)

        text_vec_model_path = kwargs.get('text_vec_model_path', config.text_vec_model_path)

        if os.path.exists(text_vec_model_path):
            self.model = Doc2Vec.load(os.path.abspath(text_vec_model_path))
            print("Parrot started")

    def remove_stopwords(self,words):
        # import jieba
        # return remove_stopwords(jieba.lcut(str1))
        return words
    def train(self,statements):
        if self.model is not None:
            self.update_model(statements)
        else:
            self.train_model(statements)

    def build_tokenzied(self,statements):
        from gensim.models.doc2vec import TaggedDocument
        tokenized = []
        for statement in statements:
            if statement.id > 0:
                tokenized.append(TaggedDocument(statement.search_text.split(' '),tags=[statement.id,statement.text]))
        return tokenized
    
    def train_model(self, statements):
        from gensim.models import Doc2Vec

        tokenized = self.build_tokenzied(statements)

        self.model = Doc2Vec(tokenized,vector_size=30,epochs=50,min_count=1,window=10,sample=1e-3,negative=5,workers=10)
        self.model.train(tokenized,total_examples=self.model.corpus_count,epochs=50)
    
    def save_model(self,save_path):
        import os
        self.model.save(os.path.join(save_path))
        
    def inferred2string(self,words):
        inferred_vector = self.model.infer_vector(doc_words=self.remove_stopwords(words))
        
        sims = self.model.dv.most_similar([inferred_vector],topn=20)
        res = []
        for sim in sims:
            if sim[1] >= self.parrot_similarity_rate:
                res.append( self.storage.get_statement_by_id(sim[0]))
        return res
    
    def update_model(self,statements):
        tokenized = self.build_tokenzied(statements)

        if len(tokenized) > 0:
            self.model.build_vocab(tokenized,update=True) #注意update = True 这个参数很重要
            self.model.train(tokenized,total_examples=self.model.corpus_count,epochs=100)