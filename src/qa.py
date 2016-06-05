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
    def __init__(self, uri, values):
        self.uri = uri
        self.values = values
        self.descr = kdb.DBPediaKnowledgeBase().get_property_descr(self.uri)

    def get_values(self):
        return self.values

    def get_descr(self):
        return self.descr

    def __str__(self):
        return self.uri + ': ' + self.descr

    def __repr__(self):
        return 'Property: ' + self.uri


class Entity:
    def __init__(self, uri, name, description, classes):
        self.uri = uri
        self.name = name
        self.description = description
        self.classes = classes
        self.main_class = classes[0] # not so wise, but sufficient
        self.properties = []

    def get_properties(self):
        if not self.properties:
            # fetch properties from knowledge base if they are empty
            prop_dict = kdb.DBPediaKnowledgeBase().get_entity_properties(self.uri, self.main_class)
            for key in prop_dict.keys():
                self.properties.append(Property(key, prop_dict[key]))
        return self.properties

    def get_prop_descrs(self):
        return [prop.descr for prop in self.get_properties()]

    def get_most_similar_prop(self, text_en, subject_tokens, tokens, print_top_n=5):
        # not include <main_word> in BagOfWord dictionary
        vect = TfidfVectorizer(ngram_range=(1, 3), sublinear_tf=True,
                               tokenizer=txt.QATokenizer('property', debug_info=True),
                               stop_words=subject_tokens
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
    msg_rephrase = 'Пожалуйста, перефразируйте вопрос!'
    msg_unknown_type = ('Тип вопроса не распознан. '
                        'Спросите о какой-нибудь сущности либо её свойстве.')

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
    'Что такое Днепропетровск?'
    'Кто такой Авраам Линкольн?'
    'Днепропетровск'
    """

    def __init__(self, text_ru):
        super().__init__(text_ru)
        self.subject_ru = self.find_subject(self.text_ru)
        self.subject_en = self.translator.translate(self.subject_ru, 'en')
        uri, name, description, classes = self.search_subject(self.subject_en)
        self.main_entity = Entity(uri, name, description, classes)

    @staticmethod
    def get_pattern():
        return ['NOUN', 'Кто такой NOUN', 'Что такое NOUN']

    def get_answer(self):
        descr = self.main_entity.description
        return self.translator.translate(descr, 'ru')

    @staticmethod
    def search_subject(main_word):
        uri, name, description, classes = kdb.DBPediaKnowledgeBase().search(main_word)
        return uri, name, description, classes

    @staticmethod
    def find_subject(text_ru):
        subject_finder = txt.SubjectFinder()
        return subject_finder(text_ru)


class PropertyQuestion(Question):
    """
    Question about some property of object, e.g.:
    'Кто мэр в Павлограде?'
    'Где убили Джона Кеннеди?'
    """

    def __init__(self, text_ru):
        super().__init__(text_ru)
        self.subject_ru = self.find_subject(self.text_ru)
        self.subject_en = self.translator.translate(self.subject_ru, 'en')
        self.subject_tokens = self.tokenizer(self.subject_en)
        uri, name, description, classes = self.search_subject(self.subject_en)
        self.main_entity = Entity(uri, name, description, classes)

    @staticmethod
    def get_pattern():
        return ['* NOUN',]

    def get_answer(self):
        top_property, confidence = self.main_entity.\
            get_most_similar_prop(self.text_en, self.subject_tokens, self.tokens)
        if confidence > 0.0001:
            answer_list = top_property.get_values()
            final_answers = []
            for answ in answer_list:
                if utils.is_link(answ):
                    # TODO: здесь можно идти по ссылке и забирать ещё информацию
                    final_answer = utils.extract_link_entity(answ)
                else:
                    final_answer = answ
                # another blacklist (dbpedia can have anything unexpected)
                if final_answer not in ('*', ):
                    final_answers.append(final_answer)
            return self.translator.translate(', '.join(final_answers), 'ru')
        else:
            return self.msg_rephrase

    @staticmethod
    def search_subject(main_word):
        uri, name, description, classes = kdb.DBPediaKnowledgeBase().search(main_word)
        print('Lookup found:', uri)
        return uri, name, description, classes

    @staticmethod
    def find_subject(text_ru):
        subject_finder = txt.SubjectFinder()
        return subject_finder(text_ru)


class WrongQuestion(Question):
    """
    Question with no pattern matches.
    """

    def __init__(self, text_ru):
        super().__init__(text_ru)

    @staticmethod
    def get_pattern():
        # This pattern means: everything else goes as WrongQuestion
        return ['*']

    def get_answer(self):
        return self.msg_unknown_type


# TODO: def ask(question, debug_info=True):
if __name__ == '__main__':
    t0 = time()
    # 'Кто был научным руководителем Эйнштейна?'
    q_ru = 'Кто такой Алан Тьюринг?'
    question = QuestionCategorizer(q_ru).categorize()
    answer = question.get_answer()
    print(question, 'Answer: ' + answer, 'Time: ' + str(time() - t0), sep='\n')


def future_tests():
    # TODO: to tests

    'Где родился Ленин?'
    'Российская империя, Ульяновск'

    'Кто был научным руководителем Эйнштейна?'
    'Alfred Kleiner'

    'Кто научный руководитель Тьюринга?'
    'Чёрч, Алонзо'

    'На кого повлиял Эйнштейн?'
    'Эрнст G. Штраус, Лео Силард, Натан Розен'

    'Кто такой Эйнштейн?'
    'Albert Einstein was a German theoretical physicist'
    'part string'

    'Что такое Берлин?'
    'Berlin is the capital city of Germany '
    'part string'


    'Население Украины?'
    'error'

    'Какое ВВП Украины?'
    'not found in Lookup'

    'Какая глубина Азовского Моря?'
    'доделать определение сущностей из 2 слов (проверять первую большую букву)'