'''python script for tsne'''

import pickle
import numpy as np
import pandas as pd
from gensim.models.doc2vec import Doc2Vec
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from gensim.models import Doc2Vec
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2

if __name__ == "__main__":
    # load doc2vec
    # d2v = Doc2Vec.load('./sentences_nostem_d2v.d2v')

    # # get d2v array
    # d2v_array = np.zeros((434792, 100))
    # d2v_array[0]
    # for sx in range(434792):
    #     d2v_array[sx] = d2v.docvecs[['SENT_%s' % sx]]

    dfS_raw = pd.read_csv('d2v_array_nostem.csv',index_col='level_0')

    print('d2v array loaded')

    with open('startup_sentence_bool.pkl','rb') as f:
        startup_sentence_bool = pickle.load(f)

    # grab smaller array...
    dfS_raw = dfS_raw[startup_sentence_bool]
    d2v_array = dfS_raw[dfS_raw.columns[8:]].as_matrix()

    # dimensionality reduction
    svd = PCA()
    svd_transform = svd.fit_transform(d2v_array)
    svd_covariance = svd.get_covariance()



    # tsne
#    tsne = TSNE(n_components=5, verbose=1, random_state=0, method='exact')
#    d2v_tsne = tsne.fit_transform(d2v_array)

    # pickle the tsne object
    with open('d2v_svd_nostem.pkl','wb') as f:
        pickle.dump(svd, f)
