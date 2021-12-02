import pandas as pd

with open('raw_data.pickle', 'rb') as handle:
    raw_data = load(handle)


nlp = spacy.load('en_core_web_trf')

def preprocess(judgement_dict:dict):
    """Preprocesses individual dictionary entries 

    Args:

    Returns:

    """
    df = pd.DataFrame(columns = ['name', 'id', 'doc'] )
    keys = judgement_dict.keys()
    for key in keys:
        doc = nlp(judgement_dict[key].text)
        for a, b, c in zip([judgement_dict[key].title] * len(doc), [str(key)] * len(doc), [token for token in doc]):
            df = df.append({'name' : a, 'id': b, 'doc' : c}, ignore_index = True)
    return df
    
preprocess(raw_data)


# To-Dos:
# 1. extract metainformation from judgements
# 2. 'non-NLP'-data preperation (how many judgements over time, per article, etc.)
# 3. exploratory data analysis

# Data visualization & Communication
# Plan: data visualization & Dashboard