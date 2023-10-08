from datetime import date, datetime
import json
import re
import os
import jieba
from jionlp import remove_stopwords
from gensim.models.doc2vec import TaggedDocument
from gensim.models import Doc2Vec
from service import config
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"


def deal(list_ori,p):   
    list_new=[]				#处理后的列表，是一个二维列表
    list_short=[]			#用于存放每一段列表
    for i in list_ori:
        if i!=p:		
            list_short.append(i)
        else:
            list_new.append(list_short)
            list_short=[]
    list_new.append(list_short)   #最后一段遇不到切割标识，需要手动放入
    return list_new

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)
        
class Parrot(object):
    model = object
    history = []
    similarity_rate = 0.96
    def __init__(self, similarity_rate=0.96):
        self.similarity_rate = similarity_rate
        file_list =  os.listdir(config.SERVICE_CONFIG.parrot_model_path)
        if 'model.pkl' in file_list:
            print(os.path.join(config.SERVICE_CONFIG.parrot_model_path,'model.pkl'))
            self.model = Doc2Vec.load(os.path.join(config.SERVICE_CONFIG.parrot_model_path,'model.pkl'))
        if 'history.json' in file_list:
            with open(os.path.join(config.SERVICE_CONFIG.parrot_model_path,'history.json')) as f:
                self.history = json.load(f)
        print("Parrot started")

    def remove_stopwords(self,str1):
        return remove_stopwords(jieba.lcut(str1))

    def process_chat_history(self,file_path):
        pt = re.compile(r'(\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}) ([^(]*)\(([1-9][0-9]{4,})\)')
        msg_list = []
        nicknames = []

        file = open(file_path,encoding="utf-8").readlines()
        file = deal(file,'\n')

        for item in file:
            try:
                info = re.findall(pt,item[0])[0]
                nicknames.append(json.dumps(info[1],cls=ComplexEncoder))
                if '[图片]' not in item[1]:
                    msg_list.append({
                                        'time': datetime.strptime(info[0], "%Y-%m-%d %H:%M:%S"),
                                        'nickname': info[1],
                                        'qq': info[2],
                                        'message': item[1].replace('\n', ''),
                                    })
            except:
                pass
        jsont = json.dumps(msg_list,cls=ComplexEncoder)

        for name in nicknames:
            jsont = jsont.replace('@','')
            jsont = jsont.replace(name.replace('\"',''),'')

        jsont = json.loads(jsont)
        msg_list = []
        for item in jsont:
            item['time'] = datetime.strptime(item['time'], "%Y-%m-%d %H:%M:%S")
            msg_list.append(item)
        return msg_list
    def train_model_history(self,history_path):
        self.history = self.process_chat_history(history_path)
        sentences = [self.remove_stopwords(item['message']) for item in self.history]
        tokenized = [TaggedDocument(sentence,tags=[index]) for index,sentence in enumerate(sentences)]
        self.model = Doc2Vec(tokenized,min_count=1,window=3,sample=1e-3,negative=5,workers=4)
        self.model.train(tokenized,total_examples=self.model.corpus_count,epochs=10)
    def train_model(self, data):
        for line in data:
            self.history.append({'message' : line})
        sentences = [self.remove_stopwords(s) for s in data]
        tokenized = [TaggedDocument(sentence,tags=[index]) for index,sentence in enumerate(sentences)]
        self.model = Doc2Vec(tokenized,min_count=1,window=3,sample=1e-3,negative=5,workers=4)
        self.model.train(tokenized,total_examples=self.model.corpus_count,epochs=10)
    
    def save_model(self,save_path):
        self.model.save(os.path.join(save_path,'model.pkl'))
        with open(os.path.join(save_path,'history.json'),'w') as f:
            json.dump(self.history,f,cls=ComplexEncoder)
        
    def inferred2string(self,msg):
        inferred_vector = self.model.infer_vector(doc_words=self.remove_stopwords(msg))
        sims = self.model.dv.most_similar([inferred_vector],topn=5)
        for sim in sims:
            if len(self.history[sim[0]]) > 2 and sim[1] >= self.similarity_rate:
                return self.history[sim[0]]['message']
        return None
    
    def update_model(self,data):
        """最好是{
                    'time': "%Y-%m-%d %H:%M:%S",
                    'nickname': info,
                    qq': info,
                    'message': item,
                }
            其中message为必须的
        """
        for line in data:
            self.history.append({'message' : line})
        sentence = [self.remove_stopwords(s) for s in data]
        tokenized = [TaggedDocument(sentence,tags=[index]) for index,sentence in enumerate(sentence)]
        self.model.build_vocab(tokenized,update=True) #注意update = True 这个参数很重要
        self.model.train(tokenized,total_examples=self.model.corpus_count,epochs=100)

