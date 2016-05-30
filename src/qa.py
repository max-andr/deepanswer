from abc import abstractmethod
import src.knowledge_base as kdb
import src.text_preprocessing as prepr
from collections import defaultdict
from operator import itemgetter
from microsofttranslator import Translator, TranslateApiException
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from importlib import reload
for module in [kdb, prepr]:
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

    def get_most_similar_prop(self, question, print_top_n=5):
        # TODO: надо расширять запрос синонимами (founded -> established, humidity -> precipitation)
        # not include <main_word> in BagOfWord dictionary
        filter_list = prepr.QATokenizer('question', debug_info=True)(question.main_word)
        print(filter_list)
        vect = TfidfVectorizer(ngram_range=(1, 3), sublinear_tf=True,
                               tokenizer=prepr.QATokenizer('property', debug_info=True),
                               vocabulary=filter(lambda w: w not in filter_list, question.tokens))
        props_matrix = vect.fit_transform(self.get_prop_descrs())

        # Change tokenizer to handle questions
        vect.tokenizer = prepr.QATokenizer('question', debug_info=True)
        q_vector = vect.transform([question.text_en])
        print('Bag of words vocabulary:', vect.get_feature_names())
        sims = cosine_similarity(q_vector, props_matrix).flatten()
        top_sims = sims.argsort()[:-print_top_n - 1:-1]
        top_n_properties = itemgetter(*top_sims)(self.get_properties())
        print('Top {0} properties by Bag of Words similarity:'.format(print_top_n),
              *top_n_properties, sep='\n')
        return top_n_properties[0]

    def __str__(self):
        return self.uri + '\n'.join(self.properties)

    def __repr__(self):
        return 'Entity: ' + self.uri


class QuestionCategorizer:
    def __init__(self, text_ru):
        self.text_ru = text_ru

    def get_question_type(self):
        # TODO: логика определения типа вопроса
        # return Question subclass
        pass


class Question:
    """
    Abstract base class for different Question types.
    """
    def __init__(self, text_ru):
        self.text_ru = text_ru
        self.text_en = Translator('max-andr', '36OSL0SDYEtJCS1Z9kmDvbXkaOFeriDcB2ZvLSAA+q8=').\
            translate(text_ru, 'en')
        self.tokenizer = prepr.QATokenizer('question', debug_info=True)
        self.tokens = self.tokenizer(self.text_en)

    def __str__(self):
        return ('Question ru: ' + question.text_ru + '\n' +
                'Question en: ' + question.text_en)

    @abstractmethod
    def get_answer(self):
        pass


class BooleanQuestion(Question):
    """
    Question with True/False answer:
    'Авраам Линкольн был человеком?'
    'Днепропетровск - это город в Украине?'
    """
    def __init__(self, text_ru):
        super().__init__(text_ru)

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

    def get_answer(self):
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

    def get_answer(self):
        top_property = self.main_entity.get_most_similar_prop(question)
        return Answer(top_property)

    @staticmethod
    def find_main_entity(main_word):
        return kdb.DBPediaKnowledgeBase().search(main_word)[0]

    @staticmethod
    def find_main_word():
        # TODO: придумать алгоритм определения нахождения главного слова или конструкции
        return 'Pavlograd'


class Answer:
    def __init__(self, property):
        self.property = property

    def __str__(self):
        return 'Answer: ' + ', '.join(self.property.get_value())


# TODO: проверить, чтобы числа оставались после предобработки. Например, что произошло в 1776 году
question = PropertyQuestion('Какое население Павлограда?')
# TODO: def ask(question, debug_info=True):
# TODO: если похожесть близка к нулю - то сказать, что сорри, ответа не найдено
# TODO: достаточно медленная токенизация, подумать
answer = question.get_answer()
print(question, answer, sep='\n')

# TODO: Нужно уже задуматься о тестах, чтобы оценивать качество нововведений автоматически...

"""
"Profiler for tokenization.
NoSQL Amazon storage. Or key-value disk persistentcache. Research it and start to use smth.
Автоматическая система тестирования."
"""
# ссылки на онтологию (описания entity) разные. использовать только DBPedia?
#
# ontology описывает entity: Class, ObjectProperty, ...
# rdfs:domain - область допустимых свойств
# rdfs:range - область допустимых значений
# подготовить это всё в виде теоретической части
