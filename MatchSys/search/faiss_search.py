import os
from MatchSys.utils import get_time
from .search_adapter import SearchAdapter
import numpy as np
import faiss
import pickle
import time
class FaissSearch(SearchAdapter):
    def __init__(self,matchsys,**kwargs):
        self.matchsys = matchsys
        vector_model_path = kwargs.get('vector_model_path','data/text2vec-base-chinese')
        self.index_path = kwargs.get('index_path', 'data/Faiss/hnsw.index')
        self.base_vector_path = kwargs.get('base_vector_path','data/Faiss/vector_data')
        self.signal_file_size = kwargs.get('signal_file_size', 100000)
        self.topk = kwargs.get('topk', 5)
        from sentence_transformers import SentenceTransformer
        self.vector_model = SentenceTransformer(vector_model_path)
        self.index = None
        self.d = 768
        
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
        else:
            print('开始生成index')
            sentences = []
            ids = []
            if len(os.listdir(self.base_vector_path )) > 0:
                print('存在向量数据，跳过从数据库构建，直接读取向量构建')
                self.build_hnsw()
            else:
                for statement in self.matchsys.storage.get_all_statements():
                    ids.append(statement.id)
                    sentences.append(statement.text)
                    if len(sentences) >= self.signal_file_size:
                        self.data_process_to_file(sentences,ids=ids)
                        sentences = []
                        ids = []
                self.data_process_to_file(sentences,ids)
                self.build_hnsw()
    def save_vec_to_file(self,sentence_embeddings,ids):
        n, d = sentence_embeddings.shape
        sentence_embeddings_file_name = str(n)+"-"+str(d)+"-"+str(time.time())+"-vec_ids_data.pkl"
        ads_path = os.path.abspath(os.path.join(self.base_vector_path,sentence_embeddings_file_name))
        pickle.dump([sentence_embeddings,ids], open(ads_path, 'wb'))
        file_size = os.path.getsize(ads_path)
        print(sentence_embeddings_file_name + " %7.3f MB" % (file_size/1024/1024))
    def data_process_to_file(self,sentences,ids):
        ids = np.array(ids)
        # 加载模型，将数据进行向量化处理
        sentence_embeddings = self.vector_model.encode(sentences)
        # 将向量处理结果存储
        self.save_vec_to_file(sentence_embeddings,ids)
    
    def build_hnsw(self,**kwargs):
        files = []
        for file in os.listdir(self.base_vector_path):
            if file.endswith('-vec_ids_data.pkl'):
                ads_path = os.path.abspath(os.path.join(self.base_vector_path,file))
                files.append(open(ads_path, 'rb'))
        description = 'IDMap,HNSW32,Flat'
        self.index = faiss.index_factory(self.d, description)
        for file in files:
            sentence_embeddings,ids = pickle.load(file)
            self.index.add_with_ids(sentence_embeddings,ids)
            file.close()
        faiss.write_index(self.index,self.index_path)
    @get_time
    def get_endcode_time(self,sentences):
        return self.vector_model.encode(sentences)
    @get_time
    def search(self,input_statement):
        input_statement_list = []
        sentences = [input_statement.text]
        sentence_embeddings = self.get_endcode_time(sentences)
        result = self.index.search(sentence_embeddings,self.topk)
        result = result[1][0]
        for input_statement_id in result:
            statement = self.matchsys.storage.get_statement_by_id(int(input_statement_id))
            # statement = self.matchsys.storage.model_to_object(statement)
            input_statement_list.append(statement)
        return input_statement_list
    
    def add_to_index(self,statements,save=False):
        ids = []
        sentences = []
        for sentence in statements:
            ids.append(sentence.id)
            sentences.append(sentence.text)
        sentence_embeddings = self.vector_model.encode(sentences)
        self.index.add_with_ids(sentence_embeddings,ids)
        if save:
            self.save_vec_to_file(sentence_embeddings,ids)
        print("载入完毕，数据量", len(sentence_embeddings))
    def train(self,**kwargs):
        data = kwargs.get('data', None)
        self.add_to_index(data,save=True)
        faiss.write_index(self.index,self.index_path)