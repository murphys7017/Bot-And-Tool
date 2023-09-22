from datetime import date, datetime
import json
import re
import os
import jieba
from gensim.models.doc2vec import TaggedDocument
from gensim.models import Doc2Vec
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
    stopwords = []
    model = object
    history = []
    def __init__(self,work_path):
        file_list =  os.listdir(work_path)
        if 'stopwords.txt' in file_list:
            self.stopwords = [line.replace('\n','',1) for line in open(work_path+'/stopwords.txt',encoding='utf-8').readlines()]
        if 'model.bin' in file_list:
            self.model = Doc2Vec.load(work_path+'/model.bin')
        if 'history.json' in file_list:
            with open(work_path+'/history.json') as f:
                self.history = json.load(f)

    def remove_stopwords(self,str1):
        words = []
        for word in jieba.lcut(str1):
            if word not in self.stopwords:
                words.append(word)
        return words

    def process_chat_history(self,file_path):
        pt = re.compile(r'(\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}) ([^(]*)\(([1-9][0-9]{4,})\)')
        msg_list = []
        nicknames = []

        file = open(file_path).readlines()
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
        self.model.save(save_path+'/model.bin')
        with open(save_path+'/history.json','w') as f:
            json.dump(self.history,f,cls=ComplexEncoder)
    def inferred2string(self,msg):

        inferred_vector = self.model.infer_vector(doc_words=self.remove_stopwords(msg))
        sims = self.model.dv.most_similar([inferred_vector],topn=1)[0][0]
        return self.history[sims]['message']
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
