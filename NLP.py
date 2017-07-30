'''this is a file of NLP processing and modelling classes'''

import pandas as pd
from nltk import PorterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
import string
import re

class NLProcessor():
    '''Class with methods to get, set, store, and basically process text data'''

    def __init__(self, raw_text=[], swords=None):
        self.raw_text = raw_text
        self.processed_text = []
        self.removed_articles = []
        if swords == None:
            self.swords = stopwords.words('english')
        else:
            self.swords = swords

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

        # return in correct format
        if output_type=='list':
            return return_text  # stored as string
        elif output_type=='dataframe':
            df = pd.DataFrame(return_text,index=index,columns=columns)
            if ttype=='raw':
                df.transpose()
                df.columns = [['raw_text']]
            return df

    def process_text(self, in_text=None, break_on=['.','?','!'], stopwords='default', to_stem=True, 
                        init_split_on='database', origdb=None):
        '''does split, lower, break into ddivs, tokenize, remove swords, and stem if desired'''
        
        if in_text is None:
            in_text = self.raw_text

        if stopwords=='default':
            swords = self.swords

        # this is specifically for parsing the storage of my scraper
        if init_split_on=='database':
            if origdb is not None:
                if '.' in break_on:
                    p_output = process_text_sentences(in_text,origdb,swords)
                else:
                    p_output = process_text_paragraphs(in_text,origdb,swords)
                atext = p_output[0]
                self.removed_articles = p_output[1]

        # this is for parsing other storages
        else:
            if '.' in break_on:
                atext = [plist_to_slist([a]) for a in in_text]
                atext = [[process_paragraph(s,swords) for s in art] for art in atext]
            else:
                atext = [a.split(break_on) for a in in_text]
                atext = [[process_paragraph(s,swords) for s in art] for art in atext]

        self.processed_text = atext
        #return atext
        
def process_paragraph(par,swords,to_stem=True):
    '''takes one paragraph (string); performs lower, tokenize, remove punctuation/stop words'''
    par = par.lower()
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(par)
    nstop_tokens = [t for t in tokens if (t not in swords and t not in string.punctuation)]
    porter = PorterStemmer()
    stokens = [porter.stem(t) for t in nstop_tokens]
    return stokens

def process_text_paragraphs(atext,origdb,swords):
    '''atext is a list or series of textstrings (one from each article), 
    origdb is a list or series of corresponding original databse IDs (ints from 0-4)'''
    # initial text split
    alist = [initial_text_split(a,int(o)) for a,o in zip(atext,origdb)]
        
    # remove very long articles
    removed_articles = [aix for aix,a in enumerate(alist) if len(a)>=250]
    alist = [a for a in alist if len(a)<250]
    
    # process each paragraph
    alist = [[process_paragraph(p,swords) for p in a] for a in alist]

    return [alist,removed_articles]

def process_text_sentences(atext,origdb,swords):
    '''same processing, but does a sentence breakup rather than paragraph'''
    # initial text split
    alist = [initial_text_split(a,int(o)) for a,o in zip(atext,origdb)]
    
    # remove very long articles
    removed_articles = [aix for aix,a in enumerate(alist) if len(a)>=250]
    alist = [a for a in alist if len(a)<250]
    
    # change paragraph splits to sentence splits
    alist = [plist_to_slist(plist) for plist in alist]
    
    # process each paragraph
    alist = [[process_paragraph(p,swords) for p in a] for a in alist]
        
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
