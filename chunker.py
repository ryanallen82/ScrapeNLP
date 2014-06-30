import nltk
from nltk.corpus.reader import PlaintextCorpusReader
from nltk.corpus import stopwords
import nltk.classify.util
from nltk.classify import NaiveBayesClassifier

import pyodbc
from random import randint

cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=R0224576\RYANSQLSERVER;DATABASE=FAQ;UID=m097654;Trusted_Connection=yes')
cursor = cnxn.cursor()

data = str(cursor.execute('select msg from FACT').fetchall())
sentences = nltk.sent_tokenize(data)
sentences = [nltk.word_tokenize(sent) for sent in sentences]
sentences = [nltk.pos_tag(sent) for sent in sentences]

f = open('chunks.txt','a')

cp = nltk.RegexpParser('CHUNK: {<WP.*|EX><NN.*>}')
for sent in sentences:
    tree = cp.parse(sent)
    for subtree in tree.subtrees():
        if subtree.node == 'CHUNK': 
            print subtree
            f.write(str(subtree))
            f.write('\n')

f.close()
