import nltk


def parts_of_speech(corpus):
    "returns named entity chunks in a given text"
    sentences = nltk.sent_tokenize(corpus)
    tokenized = [nltk.word_tokenize(sentence) for sentence in sentences]
    pos_tags  = [nltk.pos_tag(sentence) for sentence in tokenized]
    return nltk.ne_chunk_sents(pos_tags, binary=True)


def find_entities(chunks):
    "given list of tagged parts of speech, returns unique named entities"

    def traverse(tree):
        "recursively traverses an nltk.tree.Tree to find named entities"
        entity_names = []

        if hasattr(tree, 'label') and tree.label():
            if tree.label() == 'NE':
                entity_names.append(' '.join([child[0] for child in tree]))
            else:
                for child in tree:
                    entity_names.extend(traverse(child))

        return entity_names

    named_entities = []

    for chunk in chunks:
        entities = sorted(list(set([word for tree in chunk
                                    for word in traverse(tree)])))
        for e in entities:
            if e not in named_entities:
                named_entities.append(e)
    return named_entities

# text = "David Moore, a wealthy Manhattanite from Dnipropetrovsk, comes rushing into the lobby of his apartment building, carrying his comatose wife Joan in his arms. In the hospital, Joan Moore is diagnosed as suffering from insulin shock, even though she is not a diabetic. On further investigation, Green and Briscoe find out that Joan is actually suffering from Parkinson's disease?and, unbeknownst to her husband, has been receiving treatment from Dr. Richard Shipman?and suspect that her husband is either attempting to"
text = 'In which city Christopher Columbus was born?'
text = 'In which city Columbus was born?'
entity_chunks = parts_of_speech(text)
find_entities(entity_chunks)



# from spacy.en import English
# parser = English()
#
# # Let's look at the named entities of this example:
# example = "Apple's stocks dropped dramatically after the death of Steve Jobs in October."
# example = "Where was Christopher Columbus born?"
# parsedEx = parser(example)
# for token in parsedEx:
#     print(token.orth_, token.ent_type_ if token.ent_type_ != "" else "(not an entity)")
#
# print("-------------- entities only ---------------")
# # if you just want the entities and nothing else, you can do access the parsed examples "ents" property like this:
# ents = list(parsedEx.ents)
# for entity in ents:
#     print(entity.label, entity.label_, ' '.join(t.orth_ for t in entity))

