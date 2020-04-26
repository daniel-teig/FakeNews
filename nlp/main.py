from textcomparator import TextComparator
from fact import Fact
from fact import FactType
from preprocessor import PreProcessor
from dbmanager import DBManager

db_manager = DBManager()
preprocessor = PreProcessor()

fact_data = []

test_query = "Donald Trump suggested using disinfectant as a mehtod to fight coronavirus"


def compare_test_to_db(test_query):
    preprocessor = PreProcessor()
    facts = []
    with open('facts.txt', 'r') as fact_file:
        fact_data = fact_file.read().split("\n")
    for data in fact_data:
        fact = Fact(data, preprocessor.preprocess(data), FactType.TRUTH)
        facts.append(fact)

    text_comp = TextComparator()
    # text_comp.train_model(facts)
    file_name = "test"
    # text_comp.save_model(file_name)
    text_comp.load_model(file_name)
    test_fact = Fact(test_query, preprocessor.preprocess(
        test_query), FactType.TRUTH)
    return text_comp.match_fact(test_fact, facts, topn=3)


def add_test_to_existing(results):
    test_processed = preprocessor.preprocess(test_query)

    fact_id = 1  # results[0].id

    fact = db_manager.get_fact(fact_id)
    new_tokens = [
        token for token in test_processed if token not in fact.preprocessed]
    db_manager.add_to_processed(fact_id, new_tokens)


if __name__ == "__main__":
    results = compare_test_to_db(test_query)
    print(results)
