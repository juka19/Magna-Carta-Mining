import pandas as pd
import spacy
from pickle import load, dump
import re
from datetime import date
from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from spacy.tokens import DocBin


class Judgment:
    """Contains all essential information of the respective judgment

    Args:
        title (str): Title of the Judgment
        text (str): full text of the Judgment
        url (str): url of the Judgement
        case_details (dic): Dictionary of case_details
    
    Attributes:
        title (str): Title of the Judgment
        text (str): full text of the Judgment
        url (str): url of the Judgment
        case_details (dic): Dictionary of case_details

    """
    def __init__(self, title: str, ident: str, text:str, url:str, case_details: dict):
        self.title = title
        self.ident = ident
        self.text = text
        self.url = url
        self.case_details = case_details

with open('all_data_finally.pickle', 'rb') as handle:
    raw_data = load(handle)


def extract_data(raw_data):
    
    # Transform to Dataframe
    attributes = ['title', 'ident', 'text', 'url', 'case_details']
    df = pd.DataFrame([{fn: getattr(raw_data[key], fn) for fn in attributes} for key in raw_data])
    
    # Extract case details:
    df = pd.concat([
        df,
        df['case_details'].str.extract(r"(?:[Ii]mportance\s[lL]evel\n)(?P<importance_lvl>.*)(?:\n[Rr]epresented\sby|[Rr]espondent\s[sS]tate)", flags=re.S),
        df['case_details'].str.extract(r"(?:[Cc]onclusion\(s\)?\n?)(?P<conclusion>.*)(?:\n[Aa]rticle\(s\))", flags=re.S),
        df['case_details'].str.extract(r"(?:[Aa]rticle\(s\))(?P<articles>.*)(?:[Ss]eparate\s[oO]pinion\(s\))", flags=re.S),
        df['case_details'].str.extract(r"(?:[Ss]eparate\s[oO]pinion\(s\)\n?)(?P<separate_opinion>Yes|No)(?:\n[Dd]omestic\s[Ll]aw|\n[Ss]trasbourg\s[Cc]ase-[Ll]aw|\n[Kk]eywords)?", flags=re.S),
        df['case_details'].str.extract(r"(?:[kK]eywords\n)(?P<keywords>.*)(?:\nECLI)", flags=re.S),
        df['case_details'].str.extract(r"(?:[Jj]udgment\s[dD]ate\n)(?P<date>\d{2}/\d{2}/\d{4})", flags=re.S),
        df['case_details'].str.extract(r"(?:[Ss]trasbourg\s[Cc]ase-[lL]aw\n)(?P<related_cases>.*)(?:\n[Kk]eywords)", flags=re.S),
        df['case_details'].str.extract(r"(?:[Rr]espondent\s[Ss]tate\(s\)\n)(?P<respondent_state>.*)(?:\n[Jj]udgment\s[Dd]ate|[Rr]eference\s[Dd]ate)", flags=re.S)
        ], 
        axis=1
        )
    return df


def clean_data(df):
    df.dropna(inplace=True)
    df['date'] = pd.to_datetime(df['date'], errors="ignore", format="%d/%m/%Y")
    df['respondent_state'] = df['respondent_state'].str.extract(r"(?P<respondent_state>.*)")
    df['importance_lvl'] = df['importance_lvl'].str.extract(r"(?P<importance_lvl>\d|Key\scases)")
    df['the_law'] = df['text'].str.extract(r"(?:THE\sLAW)(?P<the_law>.*)(?:FOR\sTHESE\sREASONS)", flags=re.S)
    df['articles'] = [list(filter(None, re.sub('\d{1,2}-\d{1,2}-?.?', '', re.sub('(?<=P\d)-', '#', j)).replace('Rules of Court', '').split('\n'))) for j in df['articles']]
    df['related_cases'] = [re.findall(r"\d{3,5}\/\d{2}", row, flags=re.S) for row in df['related_cases']]
    pattern = "(?:[^Nn][^o])(?P<article_violation>\s[vV]iolation\sof\s(?:[Aa]rticle|[Aa]rt[.])\sP?\d{1,2})"
    df['violations'] = [re.findall(pattern=pattern, string=i, flags=re.S) if re.findall(pattern=pattern, string=i, flags=re.S) else None for i in df['conclusion']]
    pattern = "(?P<no_article_violation>[nN]o\s[vV]iolation\sof\s(?:[Aa]rticle|[Aa]rt[.])\sP?\d{1,2})"
    df['no_violations'] = [re.findall(pattern=pattern, string=i, flags=re.S) if re.findall(pattern=pattern, string=i, flags=re.S) else None for i in df['conclusion']]

    labels = []
    for v, n in zip(df['violations'], df['no_violations']):
        if n and not v:
            labels.append('no_violation')
        elif v and not n:
            labels.append('violation')
        elif not v and not n:
            labels.append('other')
        elif v and n:
            labels.append('mixed')
    df['label'] = labels
    
    df = df.loc[df['text'].str.len() < 1000000]
    return df




df = extract_data(raw_data)
df = clean_data(df)

with open('data_cleaned.pickle', 'wb') as handle:
    dump(df, handle)


df.groupby('label').size()



## create train_data
X_train, X_test, y_train, y_test = train_test_split(
    df['the_law'], df['label'], test_size=0.3, random_state=42,
    stratify=df['label']
)
train_data = [(text, label) for text, label in zip(X_train, y_train)]
test_data = [(text, label) for text, label in zip(X_test, y_test)]




nlp=spacy.load("en_core_web_sm")


def make_docs(df):
    n = 1
    docs = []
    for doc, label in nlp.pipe(df, batch_size=10, n_process=3, as_tuples=True):
        if label == 'no_violation':
            doc.cats['no_violation'] = 1
            doc.cats['violation'] = 0
            doc.cats['other'] = 0
            doc.cats['mixed'] = 0
        if label == 'violation':
            doc.cats['no_violation'] = 0
            doc.cats['violation'] = 1
            doc.cats['other'] = 0
            doc.cats['mixed'] = 0
        if label == 'other':
            doc.cats['no_violation'] = 0
            doc.cats['violation'] = 0
            doc.cats['other'] = 1
            doc.cats['mixed'] = 0
        if label == 'mixed':
            doc.cats['no_violation'] = 0
            doc.cats['violation'] = 0
            doc.cats['other'] = 0
            doc.cats['mixed'] = 1
        docs.append(doc)
        print(f"Processed {n} out of {len(df)}")
        n += 1
    return(docs)

train_docs = make_docs(train_data)
doc_bin = DocBin(docs=train_docs)
doc_bin.to_disk("./data/train.spacy")

test_docs = make_docs(test_data)
doc_bin = DocBin(docs=test_docs)
doc_bin.to_disk("./data/test.spacy")

# For training the model, go to directory, open anaconda and run python -m spacy init fill-config ./base_config.cfg ./config.cfg 
# Then, run config file: python -m spacy train config.cfg --output ./output

nlp = spacy.load("output/model-best")

y_pred = [max(nlp(text).cats, key=nlp(text).cats.get) for text in X_test]


cm = confusion_matrix(y_test, y_pred)



## NLP part
nlp = spacy.load('en_core_web_lg')
nlp.max_length = max([len(i) for i in df['text']]) + 100

docs = df['text'].tolist()

def token_filter(token):
    return not (token.is_punct | token.is_space | token.is_stop | len(token.text) <= 4)

filtered_tokens = {}
n = 1
for doc, ident in zip(nlp.pipe(docs, disable=['ner', 'tagger', 'parser'], batch_size=10, n_process=3), list(df['ident'])):
    tokens = [token for token in doc if token_filter(token)]
    filtered_tokens[ident] = tokens
    print(f'Completed iteration {n} of {len(docs)}')
    n += 1

def preprocess(judgment_dict:dict):
    """Preprocesses individual dictionary entries 

    Args:

    Returns:

    """
    df = pd.DataFrame(columns = ['name', 'id', 'doc'] )
    keys = judgment_dict.keys()
    for key in keys:
        doc = nlp(judgment_dict[key].text, batch_size=10, n_threads=3)
        for a, b, c in zip([judgment_dict[key].title] * len(doc), [str(key)] * len(doc), [token for token in doc]):
            df = df.append({'name' : a, 'id': b, 'doc' : c}, ignore_index = True)
        print(f'Processing Doc {key}, ID number: {judgment_dict[key].title}')
    return df



    
preprocess(raw_data)







# To-Dos:
# 1. extract metainformation from judgments
# 2. 'non-NLP'-data preperation (how many judgments over time, per article, etc.)
# 3. exploratory data analysis

# Data visualization & Communication
# Plan: data visualization & Dashboard

