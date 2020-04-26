import sqlite3
from fact import Fact
from fact import FactType
import config as cfg


class DBManager:

    def __init__(self, force=False):
        self.connection = sqlite3.connect(cfg.DB_FILE)
        self.sql = self.connection.cursor()
        self.create_table(force)

    def create_table(self, force=False):
        if force:
            self.sql.execute("DROP TABLE facts")
        query = """
        CREATE TABLE IF NOT EXISTS facts (
            id INTEGER PRIMARY KEY,
            content VARCHAR NOT NULL,
            preprocessed VARCHAR NOT NULL,
            fact_type INTEGER NOT NULL
        );
        """
        self.sql.execute(query)

    def add_fact(self, fact):
        query = """
        INSERT INTO facts
        VALUES (NULL,?,?,?);
        """
        fact_tuple = (fact.content, ' '.join(
            fact.preprocessed), fact.fact_type.value)
        self.sql.execute(query, fact_tuple)
        fact.id = self.sql.lastrowid
        self.connection.commit()
        return fact

    def get_all_facts(self, sorted=True):
        if sorted:
            query = """
            SELECT * FROM facts
            ORDER BY facts.id ASC;
            """
        else:
            query = """
            SELECT * FROM facts;
            """
        self.sql.execute(query)
        rows = self.sql.fetchall()
        if rows is None:
            return None
        facts = []
        for r in rows:
            facts.append(fact_from_tuple(r))
        return facts

    def get_fact(self, id):
        query = """
        SELECT * FROM facts
        WHERE facts.id = ?
        """
        self.sql.execute(query, (id,))
        result = self.sql.fetchone()
        print(result)
        if result is None:
            return None
        return fact_from_tuple(result)

    def add_to_processed(self, id, words_to_add):
        query = """
        UPDATE facts
        SET preprocessed = preprocessed || ?
        WHERE id = ?
        """
        self.sql.execute(query, (' ' + ' '.join(words_to_add), id))
        self.connection.commit()


def fact_from_tuple(fact_tuple):
    return Fact(fact_tuple[1], fact_tuple[2].split(), FactType(fact_tuple[3]), fact_tuple[0])


def test():
    db_man = DBManager()
    facts = db_man.get_all_facts()
    print(facts)
    fact1 = Fact("some content that is raw and true",
                 ["some", "content", "true"], FactType.TRUTH)
    db_man.add_fact(fact1)
    facts = db_man.get_all_facts()
    print(facts)
    fact2 = Fact("some content that is raw and false",
                 ["some", "content", "false"], FactType.FAKE)
    db_man.add_fact(fact2)
    facts = db_man.get_all_facts()
    print(facts.__str__())

    print(db_man.get_fact(1))

    db_man.add_to_processed(1, ["HELO", "250"])
    print(db_man.get_fact(1))


# test()
