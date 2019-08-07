from sklearn.datasets import fetch_20newsgroups
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
import numpy as np
from sklearn.linear_model import SGDClassifier


categories = ['alt.atheism', 'soc.religion.christian',
        'comp.graphics', 'sci.med']
my_data = fetch_20newsgroups(subset='train',
    categories=categories, shuffle=True, random_state=42)


""" Text preprocessing, tokenizing and filtering of stopwords 
are all included in CountVectorizer """
count_vect = CountVectorizer()
X_train_counts = count_vect.fit_transform(my_data.data)
X_train_counts.shape
count_vect.vocabulary_.get(u'algorithm')

tf_transformer = TfidfTransformer(use_idf=False).fit(X_train_counts)
X_train_tf = tf_transformer.transform(X_train_counts)
tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)

# Training a classifier
clf = MultinomialNB().fit(X_train_tfidf, my_data.target)
docs_new = ['God is love', 'OpenGL on the GPU is fast']
X_new_counts = count_vect.transform(docs_new)
X_new_tfidf = tfidf_transformer.transform(X_new_counts)

predicted = clf.predict(X_new_tfidf)

for doc, category in zip(docs_new, predicted):
    print('%r => %s' %(doc, my_data.target_names[category]))

# Building a pipeline

# In order to make the vetorizer => transformer => classifier easier to work with,
# scikit-learn provides a Pipeline class that behaves like a compound classifier
text_clf = Pipeline([
    ('vect', CountVectorizer()),
    ('tfidf', TfidfTransformer()),
    ('clf', MultinomialNB()),
])

twenty_test = fetch_20newsgroups(subset='test',
    categories=categories, shuffle=True, random_state=42)
docs_test = twenty_test.data
predicted = text_clf.predict(docs_test)
# accuracy of prediction
np.mean(predicted == twenty_test.target)


# using SVM

text_clf = Pipeline([
    ('vect', CountVectorizer()),
    ('tfidf', TfidfTransformer()),
    ('clf', SGDClassifier(loss='hinge', penalty='l2',
                          alpha=1e-3, random_state=42,
                          max_iter=5, tol=None)),
])

text_clf.fit(my_data.data, my_data.target)

predicted = text_clf.predict(docs_test)
np.mean(predicted == twenty_test.target)


# Evaluating the predictive accuracy of the model
text_clf = Pipeline([
    ('vect', CountVectorizer()),
    ('tfidf', TfidfTransformer()),
    ('clf', SGDClassifier(loss='hinge', penalty='l2',
                          alpha=1e-3, random_state=42,
                          max_iter=5, tol=None)),
])

text_clf.fit(my_data.data, my_data.target)

predicted = text_clf.predict(docs_test)
np.mean(predicted == twenty_test.target)