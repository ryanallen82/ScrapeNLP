from gensim import corpora, models, similarities
from nltk.corpus import stopwords
import pyodbc

cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=R0224576\RYANSQLSERVER;DATABASE=FAQ;UID=m097654;Trusted_Connection=yes')
cursor = cnxn.cursor()

stopwords = stopwords.words('english')
limit = .80


def get_data(cursor):
	documents = cursor.execute('select msg from FACT').fetchall()
	doc_split = []
	for d in documents:
		doc_split.append(str(d))

	texts = [[word for word in d.lower().split() if word not in stopwords and word.isalpha()] for d in doc_split]
	return (texts, doc_split)

def create_tfidf(texts):
	dictionary = corpora.Dictionary(texts)
	corpus = [dictionary.doc2bow(text) for text in texts]

	tfidf = models.TfidfModel(corpus)
	corpus_tfidf = tfidf[corpus]
	return (corpus_tfidf, dictionary)

def create_lsi(corpus, dictionary, n_topics=20):
	lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=n_topics, onepass=False, power_iters=2)
	index = similarities.MatrixSimilarity(lsi[corpus])
	return (lsi, index)

def cosine_sim(doc_split, dictionary, index, lsi):
	f = open('test.txt','a')
	i = 0
	while i < len(doc_split):
		vec_bow = dictionary.doc2bow(doc_split[i].lower().split())
		vec_lsi = lsi[vec_bow] 
		similarities = index[vec_lsi]
		similarities = sorted(enumerate(similarities), key = lambda item: -item[1])
		if float(similarities[1][1]) >= limit:
			print str(doc_split[i]) + " is similar to: \n"
			f.write('\n')
			f.write(str(doc_split[i]) + " is similar to: \n")

			y = 1
			while y < 11:
				if float(similarities[y][1]) >= limit:
					print "    ",str(doc_split[similarities[y][0]]), " with a cosine similarity of ", float(similarities[y][1])
					print
					f.write('\n')
					f.write("    " + str(doc_split[similarities[y][0]]) + " with a cosine similarity of " + str(similarities[y][1]) )
					f.write('\n')
				else:
					pass
				y += 1
		i += 1

def main():
	texts, docsplit = get_data(cursor)
	tdidf_corpus, dictionary = create_tfidf(texts)
	lsi, index = create_lsi(tdidf_corpus,dictionary)
	cosine_sim(docsplit,dictionary,index,lsi)

if __name__ == "__main__":
	main()