from pickle import load
import spacy


with open('data-raw.pickle', 'rb') as handle:
    raw_data = load(handle)


nlp = spacy.load('en_core_web_trf')
doc =