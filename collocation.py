import nltk
from nltk.corpus import stopwords
from nltk.collocations import *
import pyodbc

cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=R0224576\RYANSQLSERVER;DATABASE=FAQ;UID=m097654;Trusted_Connection=yes')
cursor = cnxn.cursor()

stopwords = stopwords.words('english')

data = cursor.execute('select msg from FACT').fetchall()
tokens = nltk.word_tokenize(str(data))
text = nltk.Text(tokens)
nwords = [w.lower() for w in text if w.isalpha() and w not in stopwords]
text = nltk.Text(nwords)
