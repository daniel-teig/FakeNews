
from collections import defaultdict
from gensim import corpora
from gensim import models
from gensim import similarities
from fact import Fact
from gensim.matutils import cossim
from gensim.models import LsiModel


class TextComparator:
    def __init__(self):
        self.dictionary = None
        self.model = None
        self.index = None

    def train_model(self, facts):
        self.dictionary = corpora.Dictionary(
            [fact.preprocessed for fact in facts])
        corpus = [self.dictionary.doc2bow(fact.preprocessed) for fact in facts]
        self.model = models.LsiModel(
            corpus, num_topics=len(facts), id2word=self.dictionary)
        self.index = similarities.MatrixSimilarity(self.model[corpus])

    def save_model(self, model_name):
        self.model.save(model_name + ".model")
        self.index.save(model_name + ".index")
        self.dictionary.save_as_text(model_name + ".dict")

    def load_model(self, model_name):
        self.index = similarities.MatrixSimilarity.load(model_name + ".index")
        self.model = LsiModel.load(model_name + ".model")
        self.dictionary = corpora.Dictionary.load_from_text(
            model_name + ".dict")

    def match_fact(self, fact, facts, topn=10):
        """
        Compares a fact to a list of facts using magic

        :param fact: fact to be compared to the list of facts
        :param facts: list of facts to be compared to the fact
        :returns: sorted list of tuples in the format (fact, similarity from -1 to 1). Sorted by similarity
        """
        query = fact.preprocessed

        vec_bow = self.dictionary.doc2bow(query)
        vec_lsi = self.model[vec_bow]
        sims = self.index[vec_lsi]
        sims = sorted(enumerate(sims), key=lambda item: -item[1])
        # return [(x[0]+1, x[1]) for x in sims]  # id = index+1
        results = [(facts[int(x[0])], x[1]) for x in sims]

        return results[:topn]
