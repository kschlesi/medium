
# this calculates LSA sims for each sentence for its own article...

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from gensim import similarities
import psycopg2
import NLP
from matplotlib import pyplot as plt
import pickle
import time

def sentence_own_sim(sent_reps,index,docpos):
    '''finds similarity of ddivs (ddiv_list is list fo sents with same doc) to own doc'''
    sims = index[list(sent_reps)]
    sims = [s[docpos] for s in sims]
    return sims

if __name__ == '__main__':

    # connect to postgresql db
    username = 'kimberly'
    dbname = 'medium'
    dbe = create_engine('postgres://%s@localhost/%s'%(username,dbname))

    # read in data
    dfA = pd.read_sql('articles', dbe, index_col='postid')
    dfA = dfA.dropna(axis=0,how='any')
    dfS = pd.read_sql('sentences', dbe, index_col='level_0')

    # create NLP text, corpus, models, etc
    mText = NLP.NLModeler(list(dfA.text))
    mText.process_text(break_on=['.'], init_split_on='database', origdb=list(dfA.origdb))
    mText.make_dictionary()
    mText.load_corpus('alldoc_corpus.mm')
    mText.make_ddiv_corpus()
    mText.make_tfidf()
    mText.make_lsa()
    mscorp = mText.ddiv_corpus
    mtfidf = mText.tfidf
    lsa = mText.lsa

    # load stfidf, sentence_lsa
    pkl_file = open('stfidf.pkl', 'rb')
    stfidf = pickle.load(pkl_file)
    pkl_file.close()

    pkl_file = open('sentence_lsa.pkl', 'rb')
    sentence_lsa = pickle.load(pkl_file)
    pkl_file.close()

    pkl_file = open('dfLsa.pkl', 'rb')
    dfLsa = pickle.load(pkl_file)
    pkl_file.close()    

    # create similarity
    corpus_lsa = mText.get_corpus(ctype='lsa')
    sim_index = similarities.Similarity('.',corpus_lsa,num_features = 200)

    #ti = time.time()
    # create dfLsa
    #dfLsa = dfS.slabel.copy()
    #dfLsa['sentence_lsa'] = sentence_lsa

    # pickle
    #output = open('dfLsa_1.pkl', 'wb')
    #pickle.dump(dfLsa, output)
    #output.close()

    #tf = time.time()

    #print('lsa pickled in ')
    #print(tf-ti)

    # compute final sims
    t0 = time.time()
    #test_1 = []
    #for ax,pid in enumerate(dfA.index):
    #    if ax<1
    #    test_1.append(sentence_own_sim(dfLsa.sentence_lsa[dfS.index==pid],sim_index,int(ax)))
    #test_1 = [sentence_own_sim(dfLsa.sentence_lsa[dfS.index==pid],sim_index,int(ax))
    #  for ax,pid in enumerate(dfA.index) if int(ax) < 1]
    
    t2 = time.time()
    final_sent_sims = []
    for ax,pid in enumerate(dfA.index):
        #sixes = [ for  in enumerate(dfS.postid==pid) if ]
        for sx,bl in enumerate(dfS.postid==pid):
            if bl==True:
        #sentence_lsa[ax]. # this is len 200x2
                ssim = sim_index[sentence_lsa[sx]]
                ssim = ssim[ax]
                final_sent_sims.append(ssim)
                if ax==1:
                    t1 = time.time()
                    print('one article in :')
                    print(t1-t0)

    #final_sent_sims = [sentence_own_sim(dfLsa.sentence_lsa[dfS.index==pid],sim_index,ax)
    #  for ax,pid in enumerate(dfA.index)]
    t3 = time.time()
    print('calculated in ')
    print(t3-t2)

    #pickle them
    output = open('final_sent_sims.pkl', 'wb')
    pickle.dump(final_sent_sims, output)
    output.close()

    # # try the flattening
    # final_sent_sims_flat = [s for a in final_sent_sims for s in a]

    # # pickle again
    # output = open('final_sent_sims_flat.pkl', 'wb')
    # pickle.dump(final_sent_sims_flat, output)
    # output.close()    


