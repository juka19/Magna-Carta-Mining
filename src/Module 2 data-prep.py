import pandas as pd
import spacy
from pickle import load
import re





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

with open('sample_data__unstructured.pickle', 'rb') as handle:
    raw_data = load(handle)

def extract_data(data):
    fields = ['title', 'ident', 'text', 'url', 'case_details']
    df = pd.DataFrame([{fn: getattr(data[key], fn) for fn in fields} for key in data])
    
    # Extract judges


    details_df = df['case_details'].str.extractall(r"""
    (?:[Ii]mportance\s[lL]evel)(?P<importance_lvl>.*)(?:[Rr]epresented\sby|[Rr]espondent\s[sS]tate)
    (?:[Cc]onclusion(\(s\))?)(?P<conclusion>.*)(?:[Aa]rticle\(s\)
    (?:[Aa]rticle\(s\))(?P<articles>.*)(?:[Ss]eparate\s[oO]pinion\(s\)
    (?:[Ss]eparate\s[oO]pinion\(s\))(?P<separate_opinion>.*)(?:[Dd]omestic\s[Ll]aw)
    """, flags=re.S|re.VERBOSE)




attributes = ['title', 'ident', 'text', 'url', 'case_details']
df = pd.DataFrame([{fn: getattr(raw_data[key], fn) for fn in attributes} for key in raw_data])


df['case_details'].str.extract(r"(?:[Ii]mportance\s[lL]evel\n)(?P<importance_lvl>.*)(?:\n[Rr]epresented\sby|[Rr]espondent\s[sS]tate)", flags=re.S)
df['case_details'].str.extract(r"(?:[Cc]onclusion\(s\)?\n?)(?P<conclusion>.*)(?:\n[Aa]rticle\(s\))", flags=re.S)
df['case_details'].str.extractall(r"(?:[Aa]rticle\(s\))(?P<articles>.*)(?:[Ss]eparate\s[oO]pinion\(s\))", flags=re.S)
df['case_details'].str.extractall(r"(?:[Ss]eparate\s[oO]pinion\(s\)\n?)(?P<separate_opinion>.*)(?:\n[Dd]omestic\s[Ll]aw)", flags=re.S)
df['case_details'].str.extractall(r"(?:[kK]eywords\n)(?P<keywords>.*)(?:\nECLI)", flags=re.S)
df['case_details'].str.extractall(r"(?:[Jj]udgment\s[dD]ate\n)(?P<date>.*)(?:\n[Cc]onclusion\(s\))", flags=re.S)
df['case_details'].str.extractall(r"(?:[Ss]trasbourg\s[Cc]ase-[lL]aw\n)(?P<related_cases>.*)(?:\n[Kk]eywords)", flags=re.S)

nlp = spacy.load('en_core_web_trf')

def preprocess(judgment_dict:dict):
    """Preprocesses individual dictionary entries 

    Args:

    Returns:

    """
    df = pd.DataFrame(columns = ['name', 'id', 'doc'] )
    keys = judgment_dict.keys()
    for key in keys:
        doc = nlp(judgment_dict[key].text)
        for a, b, c in zip([judgment_dict[key].title] * len(doc), [str(key)] * len(doc), [token for token in doc]):
            df = df.append({'name' : a, 'id': b, 'doc' : c}, ignore_index = True)
    return df

    
preprocess(raw_data)




# To-Dos:
# 1. extract metainformation from judgments
# 2. 'non-NLP'-data preperation (how many judgments over time, per article, etc.)
# 3. exploratory data analysis

# Data visualization & Communication
# Plan: data visualization & Dashboard

