import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.corpus import conll2000
from nltk.chunk import conlltags2tree, tree2conlltags
from nltk.chunk import ne_chunk
from nltk import pos_tag
# IOB tags to represent chunk structures in files
from nltk.chunk import conlltags2tree, tree2conlltags
from pprint import pprint
# nltk.download('averaged_perceptron_tagger')
# nltk.download('punkt')
# nltk.download('maxent_ne_chunker')
# nltk.download('words')

def preprocess(sent):
    sent = nltk.word_tokenize(sent)
    sent = nltk.pos_tag(sent)
    return sent

ex = 'European authorities fined Google a record $5.1 billion on Wednesday for abusing its power in the mobile phone market and ordered the company to alter its practices'

sent = preprocess(ex)
pattern = 'NP: {<DT>?<JJ>*<NN>}'

# Using this pattern, we create a chunk parser and test it on our sentence.
cp = nltk.RegexpParser(pattern)
cs = cp.parse(sent)
# print(cs)

# convert the tag sequences into a chunk tree
iob_tagged = tree2conlltags(cs)
# pprint(iob_tagged)

# adds category labels such as PERSON, ORGANIZATION, and GPE
ne_tree = ne_chunk(pos_tag(word_tokenize(ex)))
# print(ne_tree)