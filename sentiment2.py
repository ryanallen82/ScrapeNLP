import nltk
from nltk.corpus.reader import PlaintextCorpusReader
from nltk.corpus import stopwords
import nltk.classify.util
from nltk.classify import NaiveBayesClassifier

import pyodbc
from random import randint

cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=R0224576\RYANSQLSERVER;DATABASE=FAQ;UID=m097654;Trusted_Connection=yes')
cursor = cnxn.cursor()

data = cursor.execute('select msg from FACT').fetchall()
tokens = nltk.word_tokenize(str(data))
text = nltk.Text(tokens)
nwords = [w.lower() for w in text if w.isalpha()]
text = nltk.Text(nwords)

corpus_root='C:\Python_workspace\FAQ Scripts\corpus'

newcorpus = PlaintextCorpusReader(corpus_root,'.*')
postxt = newcorpus.words('positive-words.txt')
negtxt = newcorpus.words('negative-words.txt')

neglist = []
poslist = []

for i in range(0,len(negtxt)):
	neglist.append('negative')

for i in range(0,len(postxt)):
	poslist.append('positive')

postagged = zip(postxt,poslist)
negtagged = zip(negtxt,neglist)

posts = []

for (word, sentiment) in postagged + negtagged:
	posts.append((word, sentiment))

def get_words(posts):
	all_words = []
	for (word, sentiment) in posts:
		all_words.extend(word)
	return all_words

def get_features(wordlist):
	wordlist = nltk.FreqDist(wordlist)
	word_features = wordlist.keys()
	return word_features

word_features = get_features(get_words(posts))

def extract_features(document):
	document_words = set(document)
	features = {}
	for word in word_features:
		features['contains(%s)' % word] = (word in document_words)
	return features

training_set = nltk.classify.util.apply_features(extract_features,posts)
classifier = NaiveBayesClassifier.train(training_set)

pos = 'I love Excel'
neg = 'Jason Gill'
rand = randint(0,len(data)-1)
test = str(data[rand])
print neg, ' is ', classifier.classify(extract_features(neg))