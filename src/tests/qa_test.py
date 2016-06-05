import unittest
from src.qa import *


class PropertyPavlograd(unittest.TestCase):
    def setUp(self):
        pass

    def test_website(self):
        given = PropertyQuestion('Вебсайт Павлограда?').get_answer()
        expected = 'http://pavlograd-official.org/'
        self.assertEqual(given, expected)

    def test_major(self):
        given = PropertyQuestion('Кто мэр Павлограда?').get_answer()
        expected = 'Ivan Metelytsia'
        self.assertEqual(given, expected)

    def test_postal_code(self):
        container = PropertyQuestion('Какой почтовый код Павлограда?').get_answer()
        member = '51400'
        self.assertIn(member, container)

    def test_population(self):
        given = int(PropertyQuestion('Какое население Павлограда?').get_answer())
        expected = 109739
        self.assertLessEqual(given - expected, 10**5)

    def test_rephrase(self):
        given = PropertyQuestion('Какой борода Павлоград?').get_answer()
        expected = 'Пожалуйста, перефразируйте вопрос!'
        self.assertEqual(given, expected)


# class PropertyLincoln(unittest.TestCase):
#     def setUp(self):
#         pass
#
#     def test_website(self):
#         given = PropertyQuestion('Вебсайт Павлограда?').get_answer()
#         expected = 'http://pavlograd-official.org/'
#         self.assertEqual(given, expected)
#
#
# class DescribeKiev(unittest.TestCase):
#     def setUp(self):
#         pass
#
#     def test_website(self):
#         given = PropertyQuestion('Вебсайт Павлограда?').get_answer()
#         expected = 'http://pavlograd-official.org/'
#         self.assertEqual(given, expected)
#
#
# class DescribeLincoln(unittest.TestCase):
#     def setUp(self):
#         pass
#
#     def test_website(self):
#         given = PropertyQuestion('Вебсайт Павлограда?').get_answer()
#         expected = 'http://pavlograd-official.org/'
#         self.assertEqual(given, expected)


class WholeQASystem(unittest.TestCase):
    def setUp(self):
        pass

    def test_website(self):
        given = QuestionCategorizer('Какой вебсайт у Павлограда?').categorize().get_answer()
        expected = 'http://pavlograd-official.org/'
        self.assertEqual(given, expected)

    def test_major(self):
        given = QuestionCategorizer('Кто мэр Павлограда?').categorize().get_answer()
        expected = 'Ivan Metelytsia'
        self.assertEqual(given, expected)
        # TODO: тесты на сущности, отличные от Павлограда и города в целом

    def test_wrong(self):
        given = QuestionCategorizer('Что такое Павлоград когда же?').categorize().get_answer()
        substr_expected = 'Тип вопроса не распознан'
        self.assertIn(substr_expected, given)


if __name__ == '__main__':
    unittest.main()
