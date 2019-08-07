# Using SpaCy
import spacy
from spacy import displacy
from collections import Counter
from pprint import pprint
import en_core_web_sm
from bs4 import BeautifulSoup
import requests
import re

nlp = en_core_web_sm.load()
doc = nlp('European authorities fined Google a record $5.1 billion on Wednesday for abusing its power in the mobile phone market and ordered the company to alter its practices')

#print words with labels attached
# pprint([(X.text, X.label_) for X in doc.ents])
# pprint([(X, X.ent_iob_, X.ent_type_) for X in doc])

def url_to_string(url):
    res = requests.get(url)
    html = res.text
    soup = BeautifulSoup(html, 'html5lib')
    for script in soup(["script", "style", 'aside']):
        script.extract()
    return " ".join(re.split(r'[\n\t]+', soup.get_text()))

ny_bb = url_to_string('https://www.nytimes.com/2018/08/13/us/politics/peter-strzok-fired-fbi.html?hp&action=click&pgtype=Homepage&clickSource=story-heading&module=first-column-region&region=top-news&WT.nav=top-news')
article = nlp(ny_bb)
# len(article.ents)

# count the labels for each word
labels = [x.label_ for x in article.ents]
# Counter(labels)

# see the most frequently used words
items = [x.text for x in article.ents]
# Counter(items).most_common(3)

sentences = [x for x in article.sents]
# to be used in jupyter notebook
# displacy.render(nlp(str(sentences[20])), jupyter=True, style='ent')

# words and parts of sents
[(x.orth_,x.pos_, x.lemma_) for x in [y
                                      for y
                                      in nlp(str(sentences[20]))
                                      if not y.is_stop and y.pos_ != 'PUNCT']]

dict([(str(x), x.label_) for x in nlp(str(sentences[20])).ents])