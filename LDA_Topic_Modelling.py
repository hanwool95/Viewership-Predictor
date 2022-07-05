from gensim import corpora
from gensim.models import LdaModel
from gensim.test.utils import datapath

import codecs
import csv

class Topic_model:
    def __init__(self):
        self.token_words = []

    def get_token_words_from_csv(self, path: str):
        with codecs.open(path, 'r') as f:
            rdr = csv.reader(f)
            next(rdr)
            for i, line in enumerate(rdr):
                self.token_words.append(line)
            print("Complete loading")

    def run(self, path: str, number_topic: int):
        id2word = corpora.Dictionary(self.token_words)
        id2word.filter_extremes(no_below=10)  # 10회 이하로 등장한 단어는 삭제
        texts = self.token_words
        corpus = [id2word.doc2bow(text) for text in texts]

        lda = LdaModel(corpus, num_topics=number_topic, id2word=id2word)

        temp_file = datapath(path)
        lda.save(temp_file)

        lda = LdaModel.load(temp_file)

        topics = lda.print_topics(num_words=10)
        for topic in topics:
            print(topic)

if __name__ == "__main__":
    model = Topic_model()
    model.get_token_words_from_csv('tokenized_word.csv')
    model.run('topic_model', 5)
