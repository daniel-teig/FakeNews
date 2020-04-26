from argparse import ArgumentParser
from fact import FactType, Fact
from dbmanager import DBManager
from textcomparator import TextComparator
from preprocessor import PreProcessor
import config as cfg
import re

db_manager = DBManager()
text_comp = TextComparator()
pre_processor = PreProcessor()


def parse_args():
    parser = ArgumentParser(description="Utility stuff")
    parser.add_argument("-l", "--load", dest="load",
                        help="facts to load to the db", metavar="FILE")
    parser.add_argument('-r', '--reset', dest="reset", action='store_true',
                        help="drops the table of the database. USE WITH CAUTION!")
    parser.add_argument('-t', '--retrain', dest="retrain", action='store_true',
                        help="retrains the magic")
    parser.add_argument('-p', '--print-database', dest="printdb", action='store_true',
                        help="prints the complete database")
    return (parser.parse_args())


def main(args):
    if args.reset:
        really = input(
            "Do you really want to reset the database? This action cannot be undone (y/N): ")
        # print(really)
        if really.lower() == "y":
            db_manager.create_table(True)
            print("database successfully reset")

    if args.load is not None:
        # load to database
        with open(args.load, 'r') as text_file:
            fact_data = text_file.read().split("\n")

        facts = []
        for data in fact_data:
            fact_type = FactType.TRUTH
            if "[fake]" in data or "[0]" in data:
                fact_type = FactType.FAKE
            
            data = re.sub("\[([^\]|]*)\]", '', data)
                
            fact = Fact(data, pre_processor.preprocess(data), fact_type)
            facts.append(fact)
        for fact in facts:
            db_manager.add_fact(fact)
        print("loaded " + str(len(facts)) + " facts to database")

    if args.retrain:
        # train and save the NN
        print("Starting to retrain the model ...")
        all_facts = db_manager.get_all_facts()
        text_comp.train_model(all_facts)
        text_comp.save_model(cfg.DEFAULT_MODEL_FILE)
        print("... retrained the model and saved to " + cfg.DEFAULT_MODEL_FILE)

    if args.printdb:
        all_facts = db_manager.get_all_facts()
        print("===== START OF DATABASE (" + str(len(all_facts)) + " rows) =====")
        for fact in all_facts:
            print(fact)
        print("===== END OF DATABASE =====")


if __name__ == "__main__":
    main(parse_args())
