from argparse import ArgumentParser
from fact import FactType
from fact import Fact
from preprocessor import PreProcessor
from textcomparator import TextComparator
from dbmanager import DBManager
import config as cfg
import json

pre_processor = PreProcessor()
text_comp = TextComparator()
db_manager = DBManager()


def parse_args():
    parser = ArgumentParser(description="Add a fact or fake fact")
    parser.add_argument("fact", choices=[
                        'truth', 'fake'], help="\"fact\" if the given text is a true fact, \"fake\" if it is a fake fact")
    parser.add_argument("-t", "--text", dest="text",
                        help="text to be added to fact database", metavar="TEXT", required=True)
    parser.add_argument("-a", "--append", dest="append", action='store_true',
                        help="flag if the fact should be compared to other facts and then appended to a matching one. (Requires further input during program execution)")
    return (parser.parse_args())


def add_new_fact(new_fact):
    # add fact to db
    new_fact = db_manager.add_fact(new_fact)
    #print("Added the following fact:", new_fact)
    # text_comp.add_single_fact(new_fact)
    # TODO retrain model
    return new_fact


def main(args):
    # preprocess
    text = args.text
    fact_type = FactType.FAKE if args.fact == "fake" else FactType.TRUTH
    new_fact = Fact(text, pre_processor.preprocess(text), fact_type)

    if not args.append:
        # just create the new fact and print the json
        print(json.dumps(add_new_fact(new_fact).to_json_object()))
        return

    # compare with facts
    text_comp.load_model(cfg.DEFAULT_MODEL_FILE)
    similar_fact_tuples = text_comp.match_fact(
        new_fact, db_manager.get_all_facts())

    similar_fact_tuples = similar_fact_tuples[:cfg.ADD_FACT_CHOOSE_AMOUNT]

    similar_fact_tuples = list(
        filter(lambda f: f[1] >= cfg.SIMILARITY_THRESHOLD, similar_fact_tuples))
    similar_facts = [fact_tuple[0] for fact_tuple in similar_fact_tuples]

    if not similar_facts:
        # no similar fact yet
        # -> create new fact
        # -> retrain model
        add_new_fact(new_fact)
    else:
        # there are similar facts:
        # -> print top facts
        print("These are facts that show similarities to the given text:")
        for fact in similar_facts:
            print(fact.id, fact.content)

        # get input from admin
        matched_fact_id = input("Type id of fact (or -1): ")

        if int(matched_fact_id) == -1:
            # admin: doesn't match any of the given facts:
            # -> create new fact
            add_new_fact(new_fact)
        else:
            # admin: matches a given fact:
            matched_fact = next(
                f for f in similar_facts if f.id == matched_fact_id)
            if matched_fact is not None:
                # append preprocess to given fact
                new_processed = [
                    proc for proc in fact.processed if proc not in matched_fact.processed]
                db_manager.add_to_processed(matched_fact_id, new_processed)
                # -> retrain model TODO (not currently possible)

                print("Added following key words to the fact: ", new_processed)
            else:
                print("The given id does not match with any of the similar facts")


if __name__ == "__main__":
    main(parse_args())
