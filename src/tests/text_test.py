import unittest
from src.text import *

class Tokenizer(unittest.TestCase):
    def setUp(self):
        self.tokenizer = QATokenizer('question')

    def test_postal_code(self):
        given = self.tokenizer('What is the postal code of Pavlograd?')
        expected = ['postal', 'code', 'pavlograd']
        self.assertEqual(given, expected)

    def test_who_question(self):
        given = self.tokenizer('Who is the major of Pavlograd?')
        expected = ['name', 'major', 'pavlograd']
        self.assertEqual(given, expected)

    def test_hard_question(self):
        question = ('How do we learn and refine a model of rhetorical and semantic '
        'concepts for use as a resource in answering these questions?')
        given = self.tokenizer(question)
        expected = ['learn', 'refine', 'model', 'rhetorical', 'semantic',
                    'concept', 'use', 'resource', 'answer', 'question']
        self.assertEqual(given, expected)


class PatternMatchingDescribeTrue(unittest.TestCase):
    def setUp(self):
        self.pattern_matcher = PatternMatcher()

    def test_only_noun(self):
        given = self.pattern_matcher('Павлоград', 'NOUN')
        expected = True
        self.assertEqual(given, expected)

    def test_only_noun_with_question_mark(self):
        given = self.pattern_matcher('Павлоград?', 'NOUN')
        expected = True
        self.assertEqual(given, expected)

    def test_only_noun_with_space(self):
        given = self.pattern_matcher(' Павлоград ', 'NOUN')
        expected = True
        self.assertEqual(given, expected)

    def test_only_noun_with_exclamation(self):
        given = self.pattern_matcher('Павлоград!', 'NOUN')
        expected = True
        self.assertEqual(given, expected)

    def test_kto_takoi_noun(self):
        given = self.pattern_matcher('Кто такой Линкольн', 'Кто такой NOUN')
        expected = True
        self.assertEqual(given, expected)

    def test_chto_takoe_noun(self):
        given = self.pattern_matcher('Что такое Киев', 'Что такое NOUN')
        expected = True
        self.assertEqual(given, expected)


class PatternMatchingDescribeFalse(unittest.TestCase):
    def setUp(self):
        self.pattern_matcher = PatternMatcher()

    def test_only_noun(self):
        given = self.pattern_matcher('Павлоград а', 'NOUN')
        expected = False
        self.assertEqual(given, expected)

    def test_kto_takoi_noun(self):
        given = self.pattern_matcher('А кто такой Линкольн', 'Кто такой NOUN')
        expected = False
        self.assertEqual(given, expected)

    def test_chto_takoe_noun(self):
        given = self.pattern_matcher('Что такое быстрый', 'Что такое NOUN')
        expected = False
        self.assertEqual(given, expected)


class PatternMatchingPropertyTrue(unittest.TestCase):
    def setUp(self):
        self.pattern_matcher = PatternMatcher()

    def test_postal_code_pavlograd(self):
        given = self.pattern_matcher('Какой почтовый код Павлограда?', '* NOUN')
        expected = True
        self.assertEqual(given, expected)

    def test_postal_code_pavlograd_with_space(self):
        given = self.pattern_matcher('Какой почтовый код Павлограда ?', '* NOUN')
        expected = True
        self.assertEqual(given, expected)

    def test_website_newyork(self):
        given = self.pattern_matcher('Какой вебсайт у Нью-Йорка?', '* NOUN')
        expected = True
        self.assertEqual(given, expected)

    def test_birth_lincoln(self):
        given = self.pattern_matcher('В какому году родился Авраам Линкольн?', '* NOUN')
        expected = True
        self.assertEqual(given, expected)


class PatternMatchingPropertyFalse(unittest.TestCase):
    def setUp(self):
        self.pattern_matcher = PatternMatcher()

    def test_garbage_after_last_noun(self):
        given = self.pattern_matcher('Какой почтовый код Павлограда да?', '* NOUN')
        expected = False
        self.assertEqual(given, expected)

    def test_adjective(self):
        given = self.pattern_matcher('В какому году родился быстрый?', '* NOUN')
        expected = False
        self.assertEqual(given, expected)

# tokenizer = QATokenizer('question')
# tokenizer('How do we learn and refine a model of rhetorical?')
if __name__ == '__main__':
    unittest.main()
