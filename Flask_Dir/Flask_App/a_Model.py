from Flask_App import NLP
import pandas as pd

def apply_model(Xtrain = 'default', model= 'rfm', thresh = 0.8):
    '''Applies model to training data from db'''

    # make predictions
    pred = model.predict_proba(Xtrain[Xtrain.columns[1:]])[:,1]
    #pred = [0.85]*Xtrain.shape[0]
    Xtrain['pred'] = pred

    # grab all sentences above threshold
    Xtop = Xtrain[Xtrain.pred>thresh]
    if Xtop.empty:
        Xtop = Xtrain
    Xtop = Xtop.sort_values('pred',ascending=False)

    print(Xtop)

    # this will eventually support grouping......
    #Xtop = Xtop.sort_values('sposition',ascending=True)

    # but for now just grab top three highlights.
    try:
        hilites = Xtop.iloc[0:3]
    except: # index out of range error
        hilites = Xtop

    return hilites[['apid','sposition']]

def get_htext(recdf=[],art_info=[]):
    '''taking highlightrecs and article info, returns htext dictionary of original sentences'''

    sText = NLP.NLProcessor(list(art_info.rawtext))
    sText.process_text(break_on='.',init_split_on='database',
                       origdb=art_info.origdb,keep_raw=True)
    sents = sText.get_text()

    # grab position
    # future support for more than one article...
    htext = [sents[0][spos] for spos in recdf.sposition]
    htext_dict = dict(enumerate(htext))
    return htext_dict

