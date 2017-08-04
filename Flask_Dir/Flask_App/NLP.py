'''this is a file of NLP processing and modelling classes'''

import pandas as pd
import string
import re

from nltk import PorterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

from gensim import corpora, models, similarities
from collections import defaultdict


class NLProcessor():
    '''Class with methods to get, set, store, and basically process text data'''

    def __init__(self, raw_text=[], swords=None, quick_input=False):
        self.raw_text = raw_text
        self.processed_text = None
        self.flat_text = None
        self.removed_articles = None
        self.word_count = None
        self.ddiv_count = None
        if swords == None:
            self.swords = stopwords.words('english')
        else:
            self.swords = swords
        if quick_input:
            self.process_text(break_on=['.'],init_split_on=None)
            self.flatten_text()

    def set_text(self, in_text, ttype='raw', single_doc=False):
        '''takes in text (a list of text per doc) and stores it'''
        if single_doc:
            in_text = [in_text]

        if ttype=='raw':
            self.raw_text = in_text

        elif ttype=='tokenized':
            self.processed_text = in_text

    def get_text(self, ttype='tokenized', output_type='list', index=None, columns=None):
        '''returns text as a list or dataframe'''
        # set return text
        if ttype=='raw':
            return_text = self.raw_text
        elif ttype=='tokenized':
            return_text = self.processed_text
        elif ttype=='flat':
            return_text = self.flat_text

        # return in correct format
        if output_type=='list':
            return return_text  # stored as string
        elif output_type=='dataframe':
            df = pd.DataFrame(return_text,index=index,columns=columns)
            if ttype=='raw' or ttype=='flat':
                df.transpose()
                #df.columns = [['text']]
            return df

    def process_text(self, in_text=None, break_on=['.','?','!'], stopwords='default', to_stem=True, 
                        init_split_on='database', origdb=None, ddiv_max_length=250,keep_raw=False):
        '''does split, lower, break into ddivs, tokenize, remove swords, and stem if desired'''
        
        if in_text is None:
            in_text = self.raw_text

        if stopwords=='default':
            swords = self.swords

        # this is specifically for parsing the storage of my scraper
        if init_split_on=='database':
            if origdb is not None:
                if '.' in break_on:
                    p_output = process_text_sentences(in_text,origdb,swords,ddiv_max_length,to_stem,keep_raw)
                else:
                    p_output = process_text_paragraphs(in_text,origdb,swords,ddiv_max_length,to_stem)
                atext = p_output[0]
                self.removed_articles = p_output[1]

        # this is for parsing other storages
        else:
            if '.' in break_on:
                atext = [plist_to_slist([a]) for a in in_text]
                atext = [[process_paragraph(s,swords,to_stem) for s in art] for art in atext]
            else:
                atext = [a.split(break_on) for a in in_text]
                atext = [[process_paragraph(s,swords,to_stem) for s in art] for art in atext]

        self.processed_text = atext
        self.word_count = sum([len(s) for s in atext])

    def flatten_text(self,text='default'):
        '''flattens text to include simply a list of all words in each corpus/article'''
        if text=='default':
            text = self.processed_text
        self.flat_text = [flatten_list_of_lists(art) for art in text]

    def make_ddiv_count(self,text='default'):
        '''finds ddiv count per article'''
        if text=='default':
            text = self.processed_text
        self.ddiv_count = [len(a) for a in text]

    def get_ddiv_count(self):
        '''returns ddiv count'''
        return self.ddiv_count

    def get_word_count(self):
        '''returns word count'''
        return self.word_count

    def get_removed_articles(self):
        '''returns removed articles'''
        return self.removed_articles


class NLCorporizer(NLProcessor):
    '''this is an NLProcessor that also creates and holds dictionaries, corpora, frequencies, etc'''

    def __init__(self, raw_text=[], swords=None, corpus_native_path='corpus.mm'):
        NLProcessor.__init__(self, raw_text, swords)
        self.frequencies = None
        self.dictionary = None
        self.corpus_native = None
        self.corpus_native_path = corpus_native_path

    def count_frequencies(self,texts='default'):
        '''counts all frequencies'''
        if texts=='default':
            if self.flat_text==None:
                self.flatten_text()
            texts = self.flat_text

        self.frequencies = defaultdict(int)
        for text in texts:
            for token in text:
                self.frequencies[token] += 1

    def get_frequencies(self):
        '''returns frequencies'''
        return self.frequencies

    def make_dictionary(self,texts='default',text_frequency_min=2):
        '''creates dictionary'''
        if self.frequencies==None:
            self.count_frequencies(texts)

        if texts=='default':
            texts = self.flat_text

        texts = [[token for token in text if self.frequencies[token] >= text_frequency_min]
                for text in texts]
        self.dictionary = corpora.Dictionary(texts)

    def get_dictionary(self):
        '''returns dictionary'''
        return self.dictionary

    def make_corpus(self,texts='default',fname='default'):
        '''takes atext, a list of lists of words per article, and a dictionary, and returns/saves corpus'''
        if texts=='default':
            texts = self.flat_text

        # check for dictionary 
        if self.dictionary==None:
            self.make_dictionary(texts=texts)

        # create corpus
        self.corpus_native = [self.dictionary.doc2bow(art) for art in texts]

        # store to disk, for later use
        if fname=='default':
            fname = self.corpus_native_path
        else:
            self.corpus_native_path = fname
        corpora.MmCorpus.serialize(fname, self.corpus_native)

    def load_corpus(self,fname='corpus.mm'):
        '''loads corpus from a given filename (.mm corpus only)'''
        if self.corpus_native==None:
            self.corpus_native = corpora.MmCorpus(fname)

    def get_corpus(self):
        '''returns native corpus'''
        return self.corpus_native


class NLModeler(NLCorporizer):
    '''This class holds models and transformations (tfidf, lsa, ...)'''

    def __init__(self, raw_text=[], swords=None, corpus_native_path='corpus.mm'):
        NLCorporizer.__init__(self, raw_text=raw_text, swords=swords, corpus_native_path=corpus_native_path)
        self.tfidf = None
        self.corpus_tfidf = None
        self.lsa = None
        self.corpus_lsa = None
        self.ddiv_corpus = None

    def make_tfidf(self,corpus='default'):
        '''creates tfidf model and corpus'''
        if corpus=='default':
            corpus = self.corpus_native

        if corpus==None:
            try:
                self.load_corpus(self.corpus_native_path)
            except:
                self.make_corpus(fname=self.corpus_native_path)
            corpus = self.corpus_native

        self.tfidf = models.TfidfModel(corpus)
        self.corpus_tfidf = self.tfidf[corpus]

    def make_lsa(self,corpus='tfidf',num_topics=200):
        '''creates lsa model and corpus'''
        if corpus=='tfidf':
            corpus = self.corpus_tfidf
        elif corpus=='native':
            corpus = self.corpus_native

        self.lsa = models.LsiModel(corpus, id2word=self.dictionary, num_topics=num_topics)
        self.corpus_lsa = self.lsa[corpus]

    def lsa(self):
        '''returns lsa model'''
        return self.lsa

    def tfidf(self):
        '''returns tfidf model'''
        return self.tfidf

    def make_ddiv_corpus(self,ptext='default'):
        '''sets ddiv corpus'''
        if ptext=='default':
            ptext = self.processed_text

        ddiv_corp = []
        for art in ptext:
            [ddiv_corp.append( self.dictionary.doc2bow(ddiv) ) for ddiv in art]
        self.ddiv_corpus = ddiv_corp

    def ddiv_corpus(self):
        '''returns ddiv corpus'''
        return self.ddiv_corpus

    def get_corpus(self,ctype='native',by_ddiv=False):
        '''returns corpus -- overrides inherited get_corpus'''
        if not by_ddiv:
            if ctype=='native':
                return self.corpus_native
            elif ctype=='tfidf':
                return self.corpus_tfidf
            elif ctype=='lsa':
                return self.corpus_lsa
        if by_ddiv:
            if self.ddiv_corpus is None:
                self.make_ddiv_corpus()
            if ctype=='native':
                return self.ddiv_corpus
            if ctype=='tfidf':
                return self.tfidf[self.ddiv_corpus]
            if ctype=='lsa':
                return self.lsa[self.tfidf[self.ddiv_corpus]]



class NLSimilarity(NLModeler):

    def __init__(self):
        NLModeler.__init__(self, raw_text=[], swords=None, corpus_native_path='corpus.mm', num_topics=200)
        self.lsa_index = None

        # try:
        #     self.load_corpus(corpus_native_path)
        # except: # type of exception...
        #     self.make_corpus(fname=corpus_native_path)

        # if self.tfidf is None:
        #     self.make_tfidf()
        # if self.lsa is None:
        #     self.make_lsa(num_topics=num_topics)

        # self.lsa_index = similarities.Similarity('.',lsa[corp],num_features = 200)



    





######## HELPER FUNCTIONS FOR PROCESSING ########
        
def process_paragraph(par,swords,to_stem=True):
    '''takes one paragraph (string); performs lower, tokenize, remove punctuation/stop words'''
    par = par.lower()
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(par)
    nstop_tokens = [t for t in tokens if (t not in swords and t not in string.punctuation)]
    if to_stem:
        porter = PorterStemmer()
        nstop_tokens = [porter.stem(t) for t in nstop_tokens]
    return nstop_tokens

def process_text_paragraphs(atext,origdb,swords,ddiv_max_length=250,to_stem=True):
    '''atext is a list or series of textstrings (one from each article), 
    origdb is a list or series of corresponding original databse IDs (ints from 0-4)'''
    # initial text split
    alist = [initial_text_split(a,int(o)) for a,o in zip(atext,origdb)]
        
    # remove very long articles
    removed_articles = [aix for aix,a in enumerate(alist) if len(a)>=ddiv_max_length]
    alist = [a for a in alist if len(a)<ddiv_max_length]
    
    # process each paragraph
    alist = [[process_paragraph(p,swords,to_stem) for p in a] for a in alist]

    return [alist,removed_articles]

def process_text_sentences(atext,origdb,swords,ddiv_max_length=250,to_stem=True,keep_raw=False):
    '''same processing, but does a sentence breakup rather than paragraph'''
    # initial text split
    alist = [initial_text_split(a,int(o)) for a,o in zip(atext,origdb)]
    
    # remove very long articles
    removed_articles = [aix for aix,a in enumerate(alist) if len(a)>=ddiv_max_length]
    alist = [a for a in alist if len(a)<ddiv_max_length]
    
    # change paragraph splits to sentence splits
    alist = [plist_to_slist(plist) for plist in alist]
    
    # process each paragraph
    if not keep_raw:
        alist = [[process_paragraph(p,swords,to_stem) for p in a] for a in alist]
        
    return [alist,removed_articles]

def initial_text_split(article_text,origdb):
    '''takes article text and original db and performs appropriate splitting'''
    if origdb in [1,2,3]:
        # split into paragraphs
        plist = article_text.split('/n')

        # remove \n symbols from within words
        plist = [p.replace('\n','') for p in plist]
        
    else:
        # split into paragraphs
        plist = article_text.split('\n')
            
    return plist

def plist_to_slist(plist):
    '''changes a list of paragraphs to a list of sentences'''
    spl = [re.split('[/./!/?]',par) for par in plist]
    return [s for p in spl for s in p if len(s)>1]

def flatten_list_of_lists(lol):
    l = []
    for s in lol:
        l.extend(s)
    return l
