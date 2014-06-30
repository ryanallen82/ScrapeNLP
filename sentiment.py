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

tagged = postagged + negtagged 

words = []

for (word,sentiment) in tagged:
	word_filter = [i.lower() for i in word.split()]
	words.append((word_filter, sentiment))

def getwords(words):
	allwords = []
	for (word,sentiment) in words:
		allwords.extend(word)
	return allwords

def getwordfeatures(listofwords):
	wordfreq = nltk.FreqDist(listofwords)
	words = wordfreq.keys()
	return words

def feature_extractor(doc):
	docwords = set(doc)
	features = {}
	for i in wordlist:
		features['contains(%s)' % i] = (i in docwords)
	return features

wordlist = [i for i in text if not i in stopwords.words('english')]
training_set = nltk.classify.apply_features(feature_extractor,words)

classifier = NaiveBayesClassifier.train(training_set)

rand = randint(0,len(data)-1)
test = data[rand]
print test, " is ", classifier.classify(feature_extractor(test))