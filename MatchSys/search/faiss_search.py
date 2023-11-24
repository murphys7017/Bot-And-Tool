import os
from MatchSys.utils import get_time
from .search_adapter import SearchAdapter
import numpy as np
import faiss

import time
class FaissSearch(SearchAdapter):
    def __init__(self,**kwargs):
        from sentence_transformers import SentenceTransformer
        self.vector_model = SentenceTransformer('data/text2vec-base-chinese')
        self.nlist = 50
        self.hnsw_index = None
        self.signal_file_size = 10000
        self.data_d = 128
    
    def get_ids(self,data_list):
        ids = []
        for index,value in enumerate(data_list):
            ids.append(index)
        # 将向量处理结果存储
        ids_file = "data/Faiss/ids_data.npy"
        np.save(ids_file, np.array(ids))
        file_size = os.path.getsize(ids_file)
        print("%7.3f MB" % (file_size/1024/1024))
    def data_process_10w(self,**kwargs):
        data_save_path = kwargs.get('data_save_path',"data/Faiss/vector_data") 
        sentences = kwargs.get('data_list',None)
        # 加载模型，将数据进行向量化处理
        sentence_embeddings = self.vector_model.encode(sentences)
        # 将向量处理结果存储
        n, d = sentence_embeddings.shape
        sentence_embeddings_file_name = str(n)+"-"+str(d)+"-"+str(time.time())+"-vec_data.npy"
        np.save(os.path.join(data_save_path,sentence_embeddings_file_name), sentence_embeddings)
        file_size = os.path.getsize(os.path.join(data_save_path,sentence_embeddings_file_name))
        print(sentence_embeddings_file_name + " %7.3f MB" % (file_size/1024/1024))
    def data_process_2_vector(self,**kwargs):
        data_save_path = kwargs.get('data_save_path',"data/Faiss/vector_data") 
        if not os.path.exists(data_save_path):
            os.mkdir(data_save_path)
        data_list = kwargs.get('data_list',None)
        file_list = kwargs.get('file_list',None)
        if data_list:
            # 加载模型，将数据进行向量化处理
            sentences = data_list
            if len(sentences) <= 100000:
                self.data_process_10w(**kwargs)
            else:
                for i in range(0, len(sentences), 100000):
                    kwargs['data_list'] = sentences[i: i + 100000]
                    self.data_process_10w(**kwargs)

        elif file_list:
            """

            """
    def build_hnsw(self,vec_path='data/Faiss/vector_data'):
        files = []
        for file in os.listdir(vec_path):
            if file.endswith('.npy'):
                files.append(os.path.join(vec_path,file))

        n,d = np.load(files[0]).shape

        description = 'IDMap,HNSW32,Flat'
        self.index = faiss.index_factory(d, description)
        self.add_data(files)
    def add_data(self,vec_path_list=None):
        for file in vec_path_list:
            sentence_embeddings = np.load(file)
            sentence_embeddings = sentence_embeddings.astype(np.float32)
            self.index.add_with_ids(sentence_embeddings,self.get_ids(sentence_embeddings))
            print(file + "载入完毕，数据量", len(sentence_embeddings))
            
    def search(self,sentences,topk=1):
        if isinstance(sentences,list):
            pass
        else:
            sentences = [sentences]
        sentence_embeddings = self.vector_model.encode(sentences)
        result = self.index.search(sentence_embeddings,topk)
        print(result)
        return result