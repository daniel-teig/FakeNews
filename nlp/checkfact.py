from argparse import ArgumentParser
from fact import Fact
from preprocessor import PreProcessor
from textcomparator import TextComparator
from dbmanager import DBManager
from fact import FactType
import config as cfg
import json

pre_processor = PreProcessor()
text_comp = TextComparator()
db_manager = DBManager()


def parse_args():
    parser = ArgumentParser(description="Check a fact.")
    parser.add_argument("-t", "--text", dest="text",
                        help="text to be checked", metavar="TEXT", required=True)
    parser.add_argument("--threshold", dest="threshold", type=float,
                        help="threshold for similar facts", metavar="THRESHOLD")
    return parser.parse_args()


def main(args):
    test_fact = Fact(args.text, pre_processor.preprocess(
        args.text), FactType.TRUTH)

    all_facts = db_manager.get_all_facts()

    text_comp.load_model(cfg.DEFAULT_MODEL_FILE)
    matches = text_comp.match_fact(test_fact, all_facts)

    best_match = matches[0]

    threshold = cfg.SIMILARITY_THRESHOLD

    if args.threshold is not None:
        threshold = args.threshold

    if best_match[1] >= threshold:
        output = {'fact': best_match[0].to_json_object(), 'similarity': float(best_match[1])}
    else:
        output = {'fact': None, 'similarity': 0.0}
        
    print(json.dumps(output))

    # print("The text is similar to \"", best_match[0].content + "\" id: " + str(
    #    best_match[0].id) + " similarity: " + str(best_match[1] + ". that means it's " + str(best_match[0].fact_type)))

    # if best_match[1] >= cfg.SIMILARITY_THRESHOLD:
    #     # a fact [1]is similar to the text
    #     print("The text is similar to \"",
    #           best_match[0].content + "\" id: " + str(best_match[0].id) + " similarity: " + str(best_match[1]))
    # else:
    #     print("No similar fact found")


if __name__ == "__main__":
    main(parse_args())
