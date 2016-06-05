import re

import nltk
import pymorphy2
from nltk.corpus import wordnet
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tag.perceptron import PerceptronTagger

import src.utils as utils


def get_wordnet_pos(tag):
    for letter, pos in {'J': wordnet.ADJ,
                        'V': wordnet.VERB,
                        'N': wordnet.NOUN,
                        'R': wordnet.ADV}.items():
        if tag.startswith(letter):
            return pos
    return None


class QATokenizer:
    def __init__(self, doc_type, debug_info=False):
        if debug_info:
            print('Tokenizer for <{0}> init...'.format(doc_type))
        self.debug_info = debug_info
        self.lemmatizer = WordNetLemmatizer()
        wordnet.ensure_loaded()
        self.tagger = PerceptronTagger()
        # Different options for different texts
        if doc_type == 'question':
            # Easy way to cover more questions
            self.substitutions = {'who': 'name',
                                  'whom': 'name',
                                  'whose': 'name',
                                  'where': 'country',
                                  'why': 'reason',
                                  'when': 'date',
                                  'site': 'website',
                                  'mayor': 'leader',
                                  'height': ['height', 'elevation'],
                                  'supervisor': ['doctoral', 'advisor'],
                                  'born': ['birth', 'date'],
                                  'birthplace': ['birth', 'place'],
                                  'population': ['population', 'total'],
                                  'founded': ['founded', 'established'],
                                  'humidity': ['humidity', 'precipitation'],
                                  'description': ['description', 'abstract']
                                  }
            self.black_list_substr = []
            self.black_list_match = ['be', 'do']
        elif doc_type == 'property':
            self.substitutions = {}
            self.black_list_substr = []
            self.black_list_match = ['be', 'do']
        else:
            raise ValueError('Other types for tokenization are not supported')
        self.step = 0

    def __call__(self, doc):
        def substitute(input_word):
            if input_word in self.substitutions:
                return self.substitutions[input_word]
            else:
                return input_word

        def is_blacklisted(input_word):
            if input_word in self.black_list_match:
                return True
            for bl_word in self.black_list_substr:
                if bl_word in input_word:
                    return True
            return False

        def handle_punctuation(tokens):
            punctuation_remove = '·：✔®№&▪-–—’◦…∙●“”•«»"#\'*+<=>?@^`{|}~'
            punctuation_space = ',‚![]()/\\.;:_%$…'
            tokens_new = []
            for token in tokens:
                for char in token:
                    if char in punctuation_space:
                        tokens_new.append(' ')
                    elif char in punctuation_remove:
                        pass
                    else:
                        tokens_new.append(char)
                tokens_new.append(' ')
            return ''.join(tokens_new).split()

        def handle_normalization(tokens):
            """
            Normalize to allowed POS: ADJ, VERB, NOUN, ADV; or delete token.
            :param tokens: list of word forms
            :return: list of normalized word forms
            """
            tokens_new = []
            for word, tag in nltk.tag._pos_tag(tokens, None, self.tagger):
                wn_tag = get_wordnet_pos(tag)
                if wn_tag:
                    normalized_word = self.lemmatizer.lemmatize(word, wn_tag)
                    tokens_new.append(normalized_word)
            return tokens_new

        def handle_blacklist(tokens):
            tokens_new = []
            for token in tokens:
                if not is_blacklisted(token):
                    tokens_new.append(token)
            return tokens_new

        def handle_substitution(tokens):
            tokens_new = []
            for token in tokens:
                subst = substitute(token)
                if type(subst) is str:
                    tokens_new.append(subst)
                elif type(subst) is list:
                    for s in subst:
                        tokens_new.append(s)
            return utils.unique_values(tokens_new)

        tokens = nltk.word_tokenize(doc.lower())
        tokens = handle_substitution(tokens)
        tokens = handle_punctuation(tokens)
        tokens = handle_normalization(tokens)
        tokens = handle_blacklist(tokens)
        tokens = handle_substitution(tokens)
        self.step += 1
        if self.debug_info:
            print(self.step, tokens)
        return tokens


class PatternMatcher:
    morph = pymorphy2.MorphAnalyzer()

    def __init__(self):
        pass

    def transform_question(self, question, pattern):
        replaces = ('?', ''), ('!', '')
        if 'NOUN' in pattern or 'VERB' in pattern:
            pos_text_list = []
            for token in nltk.word_tokenize(utils.multi_replace(question, replaces)):
                pos = str(self.morph.tag(token)[0].POS)
                if pos in ('NOUN', 'VERB'):
                    if not pos_text_list:
                        pos_text_list.append(pos)
                    else:
                        # 1 POS instead of 2 POS going one after another
                        if pos_text_list[-1] != pos:
                            pos_text_list.append(pos)
                else:
                    pos_text_list.append(token)
            pos_text = ' '.join(pos_text_list)
            return pos_text
        return question

    def __call__(self, question, pattern):
        question = question.strip()
        regex_replaces = ('*', '(.*)'),
        # regex_pattern = r'^Кто такой (.*)$'
        regex_pattern = utils.multi_replace(pattern, regex_replaces) + '$'
        question_form = self.transform_question(question, pattern)
        regex_result = re.match(regex_pattern, question_form)
        # print(question, pattern, regex_result, regex_result, sep=' | ')
        return bool(regex_result)


class SubjectFinder:
    morph = pymorphy2.MorphAnalyzer()

    def __init__(self):
        pass

    def transform_question(self, question, pattern):
        replaces = ('?', ''), ('!', '')
        if 'NOUN' in pattern or 'VERB' in pattern:
            pos_text_list = []
            for token in nltk.word_tokenize(utils.multi_replace(question, replaces)):
                pos = str(self.morph.tag(token)[0].POS)
                if pos in ('NOUN', 'VERB'):
                    if not pos_text_list:
                        pos_text_list.append(pos)
                    else:
                        # 1 POS instead of 2 POS going one after another
                        if pos_text_list[-1] != pos:
                            pos_text_list.append(pos)
                else:
                    pos_text_list.append(token)
            pos_text = ' '.join(pos_text_list)
            return pos_text
        return question

    def __call__(self, question: str) -> str:
        """
        simple heuristic
        """
        words_list, pos_list, token_list = [], [], []
        for token in nltk.word_tokenize(question):
            # pos = self.morph.tag(token)[0].POS
            parsed_word = self.morph.parse(token)[0]
            pos = parsed_word.tag.POS
            if pos is not None:
                words_list.append(parsed_word.normal_form)
                pos_list.append(pos)
                token_list.append(token)
        # 2 nouns together in the end and the first begins from big letter
        if pos_list[-2:] == ['NOUN', 'NOUN'] and token_list[-2][0].isupper():
            subject = ' '.join(words_list[-2:])
        elif pos_list[-1] == 'NOUN':
            subject = words_list[-1]
        else:
            raise Exception('Subject not found')
        return subject


# morph = pymorphy2.MorphAnalyzer()
# # question = 'Где находится Нью-Йорк?'
# question = 'В каком году родился Авраам Линкольн?'
# token_list, pos_list = [], []
# for token in nltk.word_tokenize(question):
#     pos = morph.tag(token)[0].POS
#     if pos is not None:
#         token_list.append(token)
#         pos_list.append(pos)
#
# if pos_list[-2:] == ['NOUN', 'NOUN']:
#     main_word = ' '.join(token_list[-2:])
# elif pos_list[-1] == 'NOUN':
#     main_word = token_list[-1]