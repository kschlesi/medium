'''this is a file to create a corpus'''

from gensim import corpora, models, similarities
import pickle

def make_corpus(atext,dictionary,fname='corpus.mm'):
	'''takes atext, a list of lists of words per article, and a dictionary, and returns/saves corpus'''
	# create corpus
	corpus = [dictionary.doc2bow(art) for art in atext]

	# store to disk, for later use
	corpora.MmCorpus.serialize(fname, corpus)

	return corpus

def get_corpus(fname='corpus.mm'):
	'''loads and returns corpus'''

	corpus = corpora.MmCorpus(fname)

	return corpus

if __name__ == '__main__':

	# create the corpus elsewhere
	pkl_file = open('atext.pkl', 'rb')
	atext = pickle.load(pkl_file)
	pkl_file.close()

	pkl_file = open('dicty.pkl', 'rb')
	dictionary = pickle.load(pkl_file)
	pkl_file.close()
	
	# save it ...
	corp = make_corpus(atext,dictionary,'atext_train_corp.mm')
