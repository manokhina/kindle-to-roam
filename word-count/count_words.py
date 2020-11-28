import argparse
import itertools
import os
import pymorphy2
import re
import nltk

from collections import Counter
from nltk.corpus import stopwords
from nltk.corpus.reader import PlaintextCorpusReader
from nltk.stem import WordNetLemmatizer

nltk.download('stopwords')
nltk.download('wordnet')


class WordCounter:
    management_words = {'tag', 'status', 'author', 'metadata', 'type', 'source', 'hiccup', 'hr'}
    trash_rus = {'это', 'который', 'этот', 'такой'}

    def __init__(self, markdown_path):
        self.markdown_path = markdown_path
        self.corpus = None
        self.words = None
        self.page_names = None
        self.texts = None

    def get_corpus(self):
        self.corpus = PlaintextCorpusReader(self.markdown_path, ".*")

    def get_page_names(self):
        self.page_names = {doc.strip(".md").lower()
                           for doc in os.listdir(self.markdown_path) if doc.endswith(".md")}

    def clean_corpus(self):
        stop_words = set(stopwords.words('english')).union(set(stopwords.words('russian')),
                                                           self.management_words, self.trash_rus,
                                                           self.page_names)  # should I delete those?
        lemmatizer = WordNetLemmatizer()
        rus_lemmatizer = pymorphy2.MorphAnalyzer()
        self.words = self.corpus.words()
        pattern = r"\w+"
        self.words = [re.findall(pattern, word) for word in self.words]
        self.words = list(itertools.chain(*self.words))
        self.words = [w.lower() for w in self.words]
        self.words = [lemmatizer.lemmatize(word) for word in self.words]
        self.words = [rus_lemmatizer.parse(word)[0].normal_form for word in self.words]
        self.words = [word for word in self.words
                      if word not in stop_words]

    def count_words(self, num_top):
        counter = Counter(self.words)
        top_words = counter.most_common(num_top)
        for word, num in top_words:
            print(word, num)

    def run(self, top_n):
        self.get_corpus()
        self.get_page_names()
        self.clean_corpus()
        self.count_words(top_n)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--markdown_path', type=str, nargs='?', default="../kindle-to-roam/markdown",
                        help='path for retrieving markdown files')
    parser.add_argument('--n', type=int, nargs='?', default=100,
                        help='number of top words')

    args = parser.parse_args()
    word_counter = WordCounter(args.markdown_path)
    word_counter.run(args.n)
