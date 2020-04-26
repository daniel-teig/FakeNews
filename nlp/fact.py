from enum import Enum


class FactType(Enum):
    TRUTH = 1
    FAKE = 0


class Fact:
    def __init__(self, content, preprocessed, fact_type, id=-1):
        self.content = content
        self.preprocessed = preprocessed
        self.fact_type = fact_type
        self.id = id

    def to_json_object(self):
        return {'id': self.id, 'content': self.content,
                'preprocessed': self.preprocessed, 'fact_type': self.fact_type.value}

    def __str__(self):
        return "Fact: {id: %s | content: %s | preproc: %s | type: %s}" % (self.id, self.content, self.preprocessed, self.fact_type)

    def __repr__(self):
        return "Fact: {id: %s | content: %s | preproc: %s | type: %s}" % (self.id, self.content, self.preprocessed, self.fact_type)
