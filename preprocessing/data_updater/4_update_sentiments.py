# -*- coding: utf-8 -*-
import datetime as dt
import requests
import time
import json
import random
import sys
from configs import ApplicationConfig
from solr_class import *

from util import get_sentiments, get_language

SLEEP_TIME = 3
SUPPORTED_LANGUAGES = {"OtherLanguages": "OtherLanguages", 'arabic': 'ar', 'english': 'en', 'french': 'fr', 'german':'de', 'hindi':'hi', 'italian': 'it', 'spanish': 'sp', 'portuguese': 'pt'}
SUPPORTED_LANGUAGES_REVERSE = {v: k for k, v in SUPPORTED_LANGUAGES.items()}

if __name__== "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--core', help="please specify core", default=None)
    
    args = parser.parse_args()
    core = args.core

    solr = SolrClass({})

    if core != None:

        tweets_all, max_row = solr.get_no_sentiment_items(core)

        tweets_list = []
        sentiments_list = dict()

        while len(tweets_all)> 0:
            print(f'[update_sentiments]: Solr query results gotten ... {max_row}')
            print(f'[update_sentiments]: Total tweets to analyze: {len(sentiments_list)}')
            print(f'[update_sentiments]: Total tweets ready to send back to Solr: {len(tweets_list)}')

            for tweet in tweets_all:
                try:
                    if 'full_text' in tweet.keys():
                        if 'language_twitter' not in tweet.keys():
                            language_ = get_language(tweet['full_text'])
                        else:
                            if 'language' in tweet.keys():
                                language_ = get_language(tweet['full_text']) if tweet['language'] != tweet['language_twitter'] else tweet['language']
                            else:
                                language_ = get_language(tweet['full_text'])
                    else:
                        language_ = "NonText"

                    if language_ in SUPPORTED_LANGUAGES.keys():
                        sentiments_list[tweet["id"]] = {'id': tweet['id'], "full_text": tweet['full_text'], "language":SUPPORTED_LANGUAGES[language_]}
                    elif language_ in SUPPORTED_LANGUAGES_REVERSE.keys():
                        sentiments_list[tweet["id"]] = {'id': tweet['id'], "full_text": tweet['full_text'], "language":language_}
                    else:
                        tweets_list.append({'id': tweet['id'], 'sentiment': 'NonText' if language_ == 'NonText' else 'OtherLanguages', 'language':language_, 'sentiment_s':'Done'})
                except Exception as exp:
                    print(f'[update_sentiments]: [Exception] at Loading data! {exp}')
                threshold = min(4000, max_row)
                if len(tweets_list) + len(sentiments_list) >= threshold:
                    print(f'[update_sentiments]: Sentiment loaded with {threshold} tweets')
                    extracted_sentiments = None
                    try:
                        print("[update_sentiments]: Getting sentiments started")
                        extracted_sentiments = get_sentiments(sentiments_list)
                        print("[update_sentiments]: Getting sentiments done!")
                    except:
                        print('[update_sentiments]: [Exception] at calling getting_sentiments')
                        time.sleep(1)
                        pass
                    if extracted_sentiments != None:
                        for k in extracted_sentiments.keys():
                            tweets_list.append({'id': k, 'sentiment': extracted_sentiments[k], 'language':SUPPORTED_LANGUAGES_REVERSE[sentiments_list[k]['language']], 'sentiment_s':'Done'})
                        sentiments_list = dict()
                threshold = min(8000, max_row)
                
                if len(tweets_list) >= threshold:
                    print(f"[update_sentiments]: sample tweets: {[s['id'] for s in tweets_list[-3:]]}")
                    tweets_list =  solr.add_items_to_solr(core, tweets_list)
                    print(f'[update_sentiments]: {threshold} tweets written to solr')
                    time.sleep(5) #Wait for the Solr's soft commit.

            tweets_all, max_row = solr.get_no_sentiment_items(core)

        if len(sentiments_list) > 0:
            extracted_sentiments = None
            try:
                extracted_sentiments = get_sentiments(sentiments_list)
                if extracted_sentiments != None:
                    for k in extracted_sentiments.keys():
                        tweets_list.append({'id': k, 'sentiment': extracted_sentiments[k], 'language':SUPPORTED_LANGUAGES_REVERSE[sentiments_list[k]['language']], 'sentiment_s':'Done'})
            except:
                print('[update_sentiments]: [Exception] at calling getting_sentiments 2')
                pass
            finally:
                sentiments_list = dict()

        if len(tweets_list) > 0:
            print(f"[update_sentiments]: sample tweets: {tweets_list[0:3]}")
            tweets_list =  solr.add_items_to_solr(core, tweets_list)
            print('[update_sentiments]: written to solr')
        print('[update_sentiments]: Done!')
    else:
        print('Please enter core name. You can use the flag (c) to pass its name as following: \n\tpython update_sentiments.py\n')
