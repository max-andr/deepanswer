import re
import nltk
from nltk.corpus import wordnet
from nltk.stem.wordnet import WordNetLemmatizer


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
        # Different options for different texts
        if doc_type == 'question':
            self.substitutions = {'site': 'website',
                                  'mayor': 'leader',
                                  'who': 'name',
                                  'whom': 'name',
                                  'whose': 'name',
                                  'where': 'country',
                                  'why': 'reason',
                                  'when': 'date'}
            self.black_list_substr = []
            self.black_list_match = ['be']
        elif doc_type == 'property':
            self.substitutions = {}
            self.black_list_substr = []
            self.black_list_match = ['be']
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
            for word, tag in nltk.pos_tag(tokens):
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
            return [substitute(token) for token in tokens]

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

