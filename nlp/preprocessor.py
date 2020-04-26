from nltk.stem import SnowballStemmer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from num2words import num2words
import nltk


def is_number(x):
    try:
        float(x)
        return True
    except ValueError:
        return False


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


class PreProcessor:

    def __init__(self):
        # nltk.download('wordnet')
        # nltk.download('stopwords')
        self.tokenizer = RegexpTokenizer(r'\d+\.\d+|\w+')
        #self.stemmer = SnowballStemmer("english")
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words("english"))
        pass

    def preprocess(self, raw):

        raw = raw.lower()
        words = self.tokenizer.tokenize(raw)
        words = [self.lemmatizer.lemmatize(w) for w in words]
        words = [w for w in words if w not in self.stop_words]

        for i, w in enumerate(words):
            if is_number(w):
                num = float(w) if is_float(w) else int(w)
                words[i] = num2words(num)
                words[i] = words[i].replace(',', '')
                words[i] = words[i].replace(' ', '_')
        return words


def test():
    pre_proc = PreProcessor()
    pre_proc.test()
    raw = "Programmers program with 42.123 programming languages. That's it #thuglife ..."
    words = self.preprocess(raw)
    print(words)


# test()
