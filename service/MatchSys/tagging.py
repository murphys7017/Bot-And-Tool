import jieba
import os

class ChineseTagger(object):
    def __init__(self, user_dict=None):


        if user_dict is not None:
            jieba.load_userdict(os.path.abspath(user_dict))

    def get_text_index_string(self, text):
        """
        Return a string of text containing part-of-speech, lemma pairs.
        """
        bigram_pairs = []
        bigram_pairs = jieba.lcut_for_search(text)

        return ' '.join(bigram_pairs)
