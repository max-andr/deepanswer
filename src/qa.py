from abc import abstractmethod
from functools import lru_cache
from importlib import reload
from operator import itemgetter

from microsofttranslator import Translator
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import src.knowledge_base as kdb
import src.text as txt
import src.utils as utils

for module in [kdb, txt, utils]:
    reload(module)


class EntityNotFoundError(Exception):
    pass


class LowAnswerConfidenceError(Exception):
    pass


class EmptyPropertyDescriptionsError(Exception):
    pass


class UnknownQuestionTypeError(Exception):
    pass


class Property:
    def __init__(self, uri, values, fl_get_descr=True):
        self.uri = uri
        self.values = values
        self.fl_get_descr = fl_get_descr
        self.descr = kdb.DBPediaKnowledgeBase().get_property_descr(self.uri) if fl_get_descr else ''

    def get_uri(self):
        return self.uri

    def get_values(self):
        return self.values

    def get_descr(self):
        return self.descr

    def __str__(self):
        return self.uri + ': ' + self.descr

    def __repr__(self):
        return 'Property: ' + self.uri


class Entity:
    def __init__(self, uri, name, description, classes, fl_prop_descr=True):
        self.uri = uri
        self.name = name
        self.description = description
        self.classes = classes
        self.fl_prop_descr = fl_prop_descr
        self.properties = []

    def get_properties(self):
        # fetch properties from knowledge base if they are empty
        if not self.properties:
            for cls in self.classes:
                prop_dict = kdb.DBPediaKnowledgeBase().get_entity_properties(self.uri, cls)
                if prop_dict != {}:
                    for key in prop_dict.keys():
                        self.properties.append(Property(key, prop_dict[key], self.fl_prop_descr))
                    # Take only first <cls> that gives result after SPARQL query
                    break
        return self.properties

    def get_image_link(self):
        for prop in self.get_properties():
            if prop.get_uri() == 'http://dbpedia.org/ontology/thumbnail':
                return prop.get_values()[0]
        return None

    def get_prop_descrs(self):
        return [prop.descr for prop in self.get_properties()]

    def get_most_similar_prop(self, text_en, subject_tokens, tokens, print_top_n=5):
        # not include <main_word> in BagOfWord dictionary
        vect = TfidfVectorizer(ngram_range=(1, 3), sublinear_tf=True,
                               tokenizer=txt.QATokenizer('property', debug_info=True),
                               stop_words=subject_tokens)
        prop_descrs = self.get_prop_descrs()
        if prop_descrs:
            props_matrix = vect.fit_transform(prop_descrs)

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
        first_letter = text_ru.strip()[0].capitalize()
        other_letters = text_ru.strip()[1:]
        self.text_ru = first_letter + other_letters
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
    msg_entity_not_found = 'Указанная сущность не была найдена. Пожалуйста, перефразируйте вопрос!'
    msg_entity_not_recognized = 'Указанная сущность не была распознана. Пожалуйста, перефразируйте вопрос!'
    msg_property_not_found = 'Указанное свойство сущности не было найдено. Пожалуйста, перефразируйте вопрос!'
    msg_unknown_type = 'Тип вопроса не распознан. Спросите о какой-нибудь сущности либо её свойстве.'
    msg_no_property_descriptions = 'Указанная сущность не имеет свойств. Пожалуйста, задайте вопрос о другой сущности.'

    def __init__(self, text_ru):
        self.text_ru = text_ru
        self.text_en = translate(self.translator, text_ru, 'en')
        self.tokenizer = txt.QATokenizer('question', debug_info=True)
        self.tokens = self.tokenizer(self.text_en)

    def __str__(self):
        return ('Question type: ' + str(self.__class__) + '\n' +
                'Question ru: ' + self.text_ru + '\n' +
                'Question en: ' + self.text_en)

    @staticmethod
    @abstractmethod
    def get_pattern():
        pass

    @abstractmethod
    def get_answer(self, lang):
        pass

    def get_image(self):
        return ''


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
        self.subject_en = translate(self.translator, self.subject_ru, 'en')
        uri, name, description, classes = self.search_subject(self.subject_en)
        self.main_entity = Entity(uri, name, description, classes, fl_prop_descr=False)

    @staticmethod
    def get_pattern():
        return ['NOUN', 'Кто такой NOUN', 'Что такое NOUN']

    def get_answer(self, lang='ru'):
        descr = self.main_entity.description
        if descr:
            if lang == 'en':
                return descr
            else:
                return translate(self.translator, descr, lang)
        else:
            raise EntityNotFoundError(self.msg_entity_not_found)

    def get_image(self):
        image_link = self.main_entity.get_image_link()
        return image_link if image_link else ''

    def search_subject(self, main_word):
        result = kdb.DBPediaKnowledgeBase().search(main_word)
        if result:
            return result
        else:
            raise EntityNotFoundError(self.msg_entity_not_found)

    def find_subject(self, text_ru):
        subject_finder = txt.SubjectFinder()
        result = subject_finder(text_ru)
        if result:
            return result
        else:
            raise EntityNotFoundError(self.msg_entity_not_recognized)


class PropertyQuestion(Question):
    """
    Question about some property of object, e.g.:
    'Кто мэр в Павлограде?'
    'Где убили Джона Кеннеди?'
    """

    def __init__(self, text_ru):
        super().__init__(text_ru)
        self.subject_ru = self.find_subject(self.text_ru)
        self.subject_en = translate(self.translator, self.subject_ru, 'en')
        self.subject_tokens = self.tokenizer(self.subject_en)
        uri, name, description, classes = self.search_subject(self.subject_en)
        self.main_entity = Entity(uri, name, description, classes)
        top_property_result = self.main_entity.get_most_similar_prop(self.text_en, self.subject_tokens, self.tokens)
        if top_property_result:
            self.top_property, self.answer_confidence = top_property_result
        else:
            raise EmptyPropertyDescriptionsError(self.msg_no_property_descriptions)

    @staticmethod
    def get_pattern():
        return ['* NOUN', ]

    def get_answer(self, lang='ru'):
        if self.answer_confidence > 0.0001:
            answer_list = self.top_property.get_values()
            final_answers = []
            for answ in answer_list:
                if utils.is_dbpedia_link(answ):
                    final_answer = utils.extract_link_entity(answ)
                else:
                    final_answer = answ
                # another blacklist (dbpedia can have anything unexpected)
                if final_answer not in ('*',):
                    final_answers.append(final_answer)
            answer_str = ', '.join(final_answers)
            # ru en version (how about message?)
            if lang == 'en':
                return answer_str
            else:
                return translate(self.translator, answer_str, lang)
        else:
            raise LowAnswerConfidenceError(self.msg_property_not_found)

    def get_image(self):
        image_link = self.main_entity.get_image_link()
        return image_link if image_link else ''

    def search_subject(self, main_word):
        result = kdb.DBPediaKnowledgeBase().search(main_word)
        if result:
            return result
        else:
            raise EntityNotFoundError(self.msg_entity_not_found)

    def find_subject(self, text_ru):
        subject_finder = txt.SubjectFinder()
        result = subject_finder(text_ru)
        if result:
            return result
        else:
            raise EntityNotFoundError(self.msg_entity_not_recognized)


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

    def get_answer(self, lang):
        raise UnknownQuestionTypeError(self.msg_unknown_type)


@lru_cache(maxsize=10000)
def translate(translator, text, lang):
    return translator.translate(text, lang)


@utils.timeit
@lru_cache(maxsize=10000)
def ask(q_text, language='ru'):
    try:
        question = QuestionCategorizer(q_text).categorize()
        print(question)
        answer = question.get_answer(language)
        image = question.get_image()
        print('Answer: ' + answer, 'Image: ' + image, sep='\n')
        return {'answer': answer, 'image': image}
    except (EntityNotFoundError, LowAnswerConfidenceError,
            UnknownQuestionTypeError, EmptyPropertyDescriptionsError) as e:
        answer = e.args[0]
        error = e.args[0]
        image = ''
        return {'answer': answer, 'image': image, 'error': error}


if __name__ == '__main__':
    ask('Где родился Эйнштейн?')