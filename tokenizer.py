import re
import pickle
import pandas as pd
import csv

from soynlp.noun import LRNounExtractor_v2
from soynlp.tokenizer import LTokenizer

class Tokenizer:
    def __init__(self):
        self.texts = []
        self.xlsx = None
        self.noun_scores = None
        self.tokenized_words = None

    def read_excel_get_texts(self, path: str):
        self.xlsx = pd.read_excel(path)
        self.xlsx.columns = ['index','제목','장르','요일','시간','방송 기간','연출','극본','출연','기획의도(줄거리)','시청률']

        for plan in self.xlsx['기획의도(줄거리)']:
            line = re.sub(r"[\[\]<>~]", ' ', plan)
            line = re.sub(r"['~]", ' ', line)
            line = re.sub(r'"', ' ', line)
            line = re.sub('\\W', ' ', line)
            self.texts.append(line)

    def extract_noun(self):
        print("start extracting")
        noun_extractor = LRNounExtractor_v2(verbose=True, extract_compound=False)
        nouns = noun_extractor.train_extract(self.texts)
        self.noun_scores = {noun: score.score for noun, score in nouns.items()}

    def text_to_token(self):
        ltokenizer = LTokenizer(scores=self.noun_scores)
        print("making list of words")
        tokenized_words = []
        for text in self.texts:
            conclude_sent = []
            pre_list = ltokenizer.tokenize(text, flatten=False)
            for LR_list in pre_list:
                word = LR_list[0]
                conclude_sent.append(word)
            tokenized_words.append(conclude_sent)
        self.tokenized_words = tokenized_words

    def save_noun_scores(self, path: str):
        with open(path, 'wb') as fw:
            pickle.dump(self.noun_scores, fw)
            print("dumping complete")

    def load_noun_scores(self, path: str):
        with open(path, 'rb') as fr:
            self.noun_scores = pickle.load(fr)
            print("load complete")

    def save_tokenized_words(self, path: str):
        f = open(path, 'w', newline="")
        wr = csv.writer(f)
        for word in self.tokenized_words:
            wr.writerow(word)
        f.close()

if __name__ == "__main__":
    tokenizer = Tokenizer()
    tokenizer.read_excel_get_texts('total_data.xlsx')
    # tokenizer.extract_noun()
    # tokenizer.save_noun_scores('noun_scores_dictionary.pickle')
    tokenizer.load_noun_scores('noun_scores_dictionary.pickle')
    tokenizer.text_to_token()
    tokenizer.save_tokenized_words('tokenized_word.csv')
