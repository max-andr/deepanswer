from abc import abstractmethod
from importlib import reload
from operator import itemgetter
from time import time

from microsofttranslator import Translator
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import src.knowledge_base as kdb
import src.text as txt
import src.utils as utils

for module in [kdb, txt, utils]:
    reload(module)


class Property:
    def __init__(self, uri, value):
        self.uri = uri
        self.value = value
        self.descr = kdb.DBPediaKnowledgeBase().get_property_descr(self.uri)

    def get_value(self):
        return self.value

    def get_descr(self):
        return self.descr

    def __str__(self):
        return self.uri + ': ' + self.descr

    def __repr__(self):
        return 'Property: ' + self.uri


class Entity:
    def __init__(self, uri):
        self.uri = uri
        self.properties = []

    def get_properties(self):
        if not self.properties:
            # fetch properties from knowledge base if they are empty
            prop_dict = kdb.DBPediaKnowledgeBase().get_entity_properties(self.uri)
            for key in prop_dict.keys():
                self.properties.append(Property(key, prop_dict[key]))
        return self.properties

    def get_prop_descrs(self):
        return [prop.descr for prop in self.get_properties()]

    def get_most_similar_prop(self, text_en, main_word, tokens, print_top_n=5):
        # not include <main_word> in BagOfWord dictionary
        vect = TfidfVectorizer(ngram_range=(1, 3), sublinear_tf=True,
                               tokenizer=txt.QATokenizer('property', debug_info=True),
                               stop_words=[main_word]
                               )
        props_matrix = vect.fit_transform(self.get_prop_descrs())

        # Change tokenizer to handle questions
        vect.tokenizer = txt.QATokenizer('question', debug_info=True)
        q_vector = vect.transform([text_en])
        print('Bag of words vocabulary:', vect.get_feature_names())
        sims = cosine_similarity(q_vector, props_matrix).flatten()
        top_sims = sims.argsort()[:-print_top_n - 1:-1]
        top_n_properties = itemgetter(*top_sims)(self.get_properties())
        print('Top {0} properties by Bag of Words similarity:'.format(print_top_n),
              *zip(top_n_properties, sims[top_sims]), sep='\n')
        # return Property and confidence level
        return top_n_properties[0], sims[top_sims][0]

    def __str__(self):
        return self.uri + '\n'.join(self.properties)

    def __repr__(self):
        return 'Entity: ' + self.uri


class QuestionCategorizer:
    def __init__(self, text_ru):
        self.text_ru = text_ru.strip()
        self.pattern_matcher = txt.PatternMatcher()
        self.question_types = [DescribeQuestion, PropertyQuestion, WrongQuestion]

    def categorize(self):
        scores = []
        for qtype in self.question_types:
            patterns = qtype.get_pattern()
            score = self._score_pattern_matching(self.text_ru, patterns)
            scores.append(score)
        arg_i = utils.argmax(scores)
        categorized_qtype = self.question_types[arg_i]
        return categorized_qtype(self.text_ru)

    def _score_pattern_matching(self, text_ru, patterns):
        for pattern in patterns:
            bool_result = self.pattern_matcher(text_ru, pattern)
            if bool_result:
                return True
        return False


class Question:
    """
    Abstract base class for different Question types.
    """
    translator = Translator('max-andr', '36OSL0SDYEtJCS1Z9kmDvbXkaOFeriDcB2ZvLSAA+q8=')

    def __init__(self, text_ru):
        self.text_ru = text_ru
        self.text_en = self.translator.translate(text_ru, 'en')
        self.tokenizer = txt.QATokenizer('question', debug_info=True)
        self.tokens = self.tokenizer(self.text_en)

    def __str__(self):
        return ('Question type: ' + str(self.__class__) + '\n'
                'Question ru: ' + question.text_ru + '\n' +
                'Question en: ' + question.text_en)

    @staticmethod
    @abstractmethod
    def get_pattern():
        pass

    @abstractmethod
    def get_answer(self):
        pass


class DescribeQuestion(Question):
    """
    Question that give description for asked entity, e.g.:
    'Где находится Днепропетровск?'
    'Кто такой Авраам Линкольн?'
    """

    def __init__(self, text_ru):
        super().__init__(text_ru)

    @staticmethod
    def get_pattern():
        return ['NOUN', 'Кто такой NOUN', 'Что такое NOUN']

    def get_answer(self):
        # TODO: implement
        pass


class PropertyQuestion(Question):
    """
    Question about some property of object, e.g.:
    'Кто мэр в Павлограде?'
    'Где убили Джона Кеннеди?'
    """
    def __init__(self, text_ru):
        super().__init__(text_ru)
        self.main_word = self.find_main_word()
        self.main_entity_uri = self.find_main_entity(self.main_word)
        self.main_entity = Entity(self.main_entity_uri)

    @staticmethod
    def get_pattern():
        return ['* NOUN',]

    def get_answer(self):
        top_property, confidence = self.main_entity.\
            get_most_similar_prop(self.text_en, self.main_word, self.tokens)
        if confidence > 0.0001:
            return top_property.get_value()[0]
        else:
            return 'Пожалуйста, перефразируйте вопрос!'

    @staticmethod
    def find_main_entity(main_word):
        return kdb.DBPediaKnowledgeBase().search(main_word)[0]

    @staticmethod
    def find_main_word():
        # TODO: придумать алгоритм определения нахождения главного слова или конструкции
        return 'Pavlograd'


class WrongQuestion(Question):
    """
    Question with no pattern matches.
    """

    def __init__(self, text_ru):
        super().__init__(text_ru)

    @staticmethod
    def get_pattern():
        return ['*', ]

    def get_answer(self):
        return ('Тип вопроса не распознан. '
                'Спросите о какой-нибудь сущности либо её свойстве.')


# TODO: def ask(question, debug_info=True):
if __name__ == '__main__':
    t0 = time()
    # question = PropertyQuestion('Какой почтовый код Павлограда?')
    question = QuestionCategorizer('Что такое Павлоград?').categorize()
    answer = question.get_answer()
    print(question, answer, time() - t0, sep='\n')

    # TODO: если answer - это ссылка, то пойти по ней. (или выделить ответ)



