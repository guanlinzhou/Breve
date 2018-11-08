import sys
import json
import datefinder
import requests
import datetime
from gcal_uplink import *
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, KeywordsOptions, ConceptsOptions, EntitiesOptions

def get_nlu_data(samples):
    """Query IBM NLU to get keyword data for each sample."""
    data = {}
    nlu = NaturalLanguageUnderstandingV1(
        version='2018-03-16',
        username='764f1427-efb8-41b7-96b5-ab585021e5da',
        password='GwnlOQ77YmGy')
    for s in samples:
        response = nlu.analyze(
            text=s,
            language='en',
            features=Features(
                entities=EntitiesOptions(
                    emotion=True,
                    limit=5)
            ))
        data[s] = {'ent' : {}}

        for ent_data in response.result['entities']:
            if ('relevance' not in ent_data or 'emotion' not in ent_data):
                continue #yuh yeet
            data[s]['ent'][ent_data['text']] = ent_data
    return data

[{'time', 'subj', 'sender', 'body'}]

def nlu_data_processor(data):
    entities = []
    for entry in data:
        name = entry['sender']
        text = [entry['body']]
        date = datefinder.find_dates(text[0])
        for d in date:
            time = d
            if 'tomorrow' in text[0] or 'Tomorrow' in text[0]:
                time += datetime.timedelta(days = 1)
        loc = get_nlu_data(text)[text[0]]['ent']
        dict = {}
        dict['name'] = name
        dict['time'] = time
        print(time.year)
        print(time.month)
        print(time.day)
        print(time.hour)
        print(time.minute)
        print(time.second)
        print(time.microsecond)
        for x in loc:
            type = loc[x]['type']
            if type == 'Facility' or  type == 'Organization' or type == 'Location' or type == 'Geographic Feature':
                dict['location'] = loc[x]['text']
                break
        entities.append(dict)
    return entities

def run(RAW_DATA):
    data = nlu_data_processor(RAW_DATA)
    for d in data:
        print(d)
        pushToCal(d)
