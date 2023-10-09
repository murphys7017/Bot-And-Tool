from service.MatchSys import languages
import jieba
import os

class ChineseTagger(object):
    def __init__(self, language=None, user_dict=None):


        self.language = language or languages.ENG
        if user_dict is not None:
            jieba.load_userdict(os.path.abspath(user_dict))

    def get_text_index_string(self, text):
        """
        Return a string of text containing part-of-speech, lemma pairs.
        """
        bigram_pairs = []
        bigram_pairs = jieba.lcut_for_search(text)

        return ' '.join(bigram_pairs)
