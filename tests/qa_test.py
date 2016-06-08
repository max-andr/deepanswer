import unittest
from src.qa import *


class PropertyPavlograd(unittest.TestCase):
    def setUp(self):
        pass

    def test_website(self):
        given = PropertyQuestion('Какой вебсайт у Павлограда?').get_answer('en')
        expected = 'http://pavlograd-official.org/'
        self.assertEqual(given, expected)

    def test_major(self):
        given = PropertyQuestion('Кто мэр Павлограда?').get_answer('en')
        expected = 'Ivan Metelytsia'
        self.assertEqual(given, expected)

    def test_postal_code(self):
        container = PropertyQuestion('Какой почтовый код Павлограда?').get_answer('en')
        member = '51400'
        self.assertIn(member, container)

    def test_population(self):
        given = int(PropertyQuestion('Какое население Павлограда?').get_answer('en'))
        expected = 109739
        self.assertLessEqual(given - expected, 10**5)

    def test_rephrase(self):
        function_with_args = PropertyQuestion('Какой борода Павлоград?').get_answer, 'en'
        self.assertRaises(LowAnswerConfidenceError, *function_with_args)


class WholeWhoIs(unittest.TestCase):
    def test_whois_lincoln_ru_en(self):
        question = QuestionCategorizer('Кто такой Авраам Линкольн?').categorize()
        answer_en, answer_ru = question.get_answer('en'), question.get_answer('ru')
        substr_en, substr_ru = 'Abraham Lincoln', 'Авраам Линкольн'
        self.assertIn(substr_en, answer_en)
        self.assertIn(substr_ru, answer_ru)

    def test_whois_einstein_ru_en(self):
        question = QuestionCategorizer('Кто такой Эйнштейн?').categorize()
        answer_en, answer_ru = question.get_answer('en'), question.get_answer('ru')
        substr_en, substr_ru = 'Albert Einstein was', 'Альберт Эйнштейн'
        self.assertIn(substr_en, answer_en)
        self.assertIn(substr_ru, answer_ru)

    def test_whois_berlin_ru_en(self):
        question = QuestionCategorizer('Что такое Берлин?').categorize()
        answer_en, answer_ru = question.get_answer('en'), question.get_answer('ru')
        substr_en, substr_ru = 'Berlin is the capital city of Germany', \
                               'Берлин '
        self.assertIn(substr_en, answer_en)
        self.assertIn(substr_ru, answer_ru)


class WholeProperty(unittest.TestCase):
    def setUp(self):
        pass

    def test_pavlograd_website(self):
        given = QuestionCategorizer('Какой вебсайт у Павлограда?').categorize().get_answer('en')
        expected = 'http://pavlograd-official.org/'
        self.assertEqual(given, expected)

    def test_pavlograd_major(self):
        given = QuestionCategorizer('Кто мэр Павлограда?').categorize().get_answer('en')
        expected = 'Ivan Metelytsia'
        self.assertEqual(given, expected)

    def test_pavlograd_wrong(self):
        question = QuestionCategorizer('Что такое Павлоград когда же?').categorize()
        function_with_args = question.get_answer, 'en'
        self.assertRaises(UnknownQuestionTypeError, *function_with_args)



    def test_lennon_birthdate(self):
        given = QuestionCategorizer('Когда родился Джон Леннон?').categorize().get_answer('en')
        expected = '1940-10-09'
        self.assertEqual(given, expected)

    def test_lenin_birthplace_ru_en(self):
        question = QuestionCategorizer('Где родился Ленин?').categorize()
        answer_en, answer_ru = question.get_answer('en'), question.get_answer('ru')
        expected_en, expected_ru = 'Russian Empire, Ulyanovsk', 'Российская империя, Ульяновск'
        self.assertEqual(answer_en, expected_en)
        self.assertEqual(answer_ru, expected_ru)

    def test_einstein_advisor_ru_en(self):
        question = QuestionCategorizer('Кто был научным руководителем Эйнштейна?').categorize()
        answer_en, answer_ru = question.get_answer('en'), question.get_answer('ru')
        expected_en, expected_ru = 'Alfred Kleiner', 'Альфред Kleiner'
        self.assertEqual(answer_en, expected_en)
        self.assertEqual(answer_ru, expected_ru)

    def test_einstein_influenced_ru_en(self):
        question = QuestionCategorizer('На кого повлиял Эйнштейн?').categorize()
        answer_en, answer_ru = question.get_answer('en'), question.get_answer('ru')
        expected_en, expected_ru = 'Ernst G. Straus, Leo Szilard, Nathan Rosen', \
                                   'Эрнст G. Штраус, Лео Силард, Натан Розен'
        self.assertEqual(answer_en, expected_en)
        self.assertEqual(answer_ru, expected_ru)

    def test_turing_advisor_ru_en(self):
        question = QuestionCategorizer('Кто научный руководитель Тьюринга?').categorize()
        answer_en, answer_ru = question.get_answer('en'), question.get_answer('ru')
        expected_en, expected_ru = 'Alonzo Church', 'Чёрч, Алонзо'
        self.assertEqual(answer_en, expected_en)
        self.assertEqual(answer_ru, expected_ru)


if __name__ == '__main__':
    unittest.main()
