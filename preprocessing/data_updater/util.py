## -*- coding: utf-8 -*-

import requests
import time
import json
from ftlangdetect import detect
import re
import sys
import nltk
import os
import datetime
import logging
import emoji
import pandas as pd
from os.path import isfile, join
from configs import ApplicationConfig
from logging.handlers import TimedRotatingFileHandler as _TimedRotatingFileHandler
from nltk.tokenize import TweetTokenizer
tweet_tokenizer = TweetTokenizer()

LOG_FOLDER = ApplicationConfig.LOG_FOLDER
LANGUAGE_DICT = ApplicationConfig.LANGUAGE_DICT
LANGUAGE_DICT_INV = ApplicationConfig.LANGUAGE_DICT_INV

tokenizer = nltk.TweetTokenizer()

class TimedRotatingFileHandler(_TimedRotatingFileHandler):
    """
    A class to manage the backup compression.
    Args:
        _TimedRotatingFileHandler ([type]): The TimedRotatingFileHandler from loggin.handlers library.
    """
    def __init__(self, filename="", when="midnight", interval=1, backupCount=0):
        super(TimedRotatingFileHandler, self).__init__(
            filename=filename,
            when=when,
            interval=int(interval),
            backupCount=int(backupCount))
    
    def doRollover(self):
        import subprocess
        super(TimedRotatingFileHandler, self).doRollover()

def create_logger(name, level=logging.INFO, file=None):
    '''
    A function to log the events. Mainly used to manage writing to log file and to manage the files compression through TimedRotatingFileHandler class.
    
    Parameters
    ----------
    name : String
        Logger name.
    level : optional.
        level of logging (info, warning). The default is logging.INFO.
    file : String, optional
        File name, the name of the logging file. The default is None where no compression will be set in file is None.

    Returns
    -------
    logger after creation.
    '''
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logging_formatter = logging.Formatter(
        '[%(asctime)s - %(name)s - %(levelname)s] '
        '%(message)s',
        '%Y-%m-%d %H:%M:%S')
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(logging_formatter)
    logger.addHandler(ch)
    
    
    # Check whether the specified path exists or not
    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)
    if file:
        #file_handler = logging.FileHandler("{}.log".format(file))
        file_handler = TimedRotatingFileHandler(filename="../.log/{}.log".format(file), when='midnight', interval=1, backupCount=0)#when midnight, s (seconds), M (minutes)... etc
        file_handler.setFormatter(logging_formatter)
        logger.addHandler(file_handler)
    return logger

def write_data_to_file(tweets, file_name, folder = None):
    """A function to write data into a file

    Args:
        tweets (Dict or List): the dictionary of the tweets with their extracted information.
        file_name (str): the file name in which the data will be writen to.
        folder (str): the folder in which the file will be written to.
    """
    if folder != None:
        if not os.path.exists(f'../{folder}'):
            os.mkdir(f'../{folder}')
        with open(f'../{folder}/{file_name}','a+',encoding='utf-8') as fout:
            if type(tweets) == dict:
                for k in tweets.keys():
                    fout.write('%s\n'%json.dumps(tweets[k], ensure_ascii=False))
            elif type (tweet) == list:
                for tweet in tweets:
                    fout.write('%s\n'%json.dumps(tweet, ensure_ascii=False))
    else:
        with open(file_name,'a+',encoding='utf-8') as fout:
            if type(tweets) == dict:
                for k in tweets.keys():
                    fout.write('%s\n'%json.dumps(tweets[k], ensure_ascii=False))
            elif type (tweets) == list:
                for tweet in tweets:
                    fout.write('%s\n'%json.dumps(tweet, ensure_ascii=False)) 

def get_sentiments(tweets):
    """A function to access sentiment analysis service.

    'id': tweet['id'], "full_text": item["full_text"], "language"

    Args:
        tweets (dict): A dictionary of the tweets object. It should have the following keys:
        1) 'id': tweet id, 
        2) 'full_text': the full_text of the tweet,
        3) 'language': the detected language of the tweet.

    Returns:
        dict: A dictionary that hold the sentiment information as retrived from its service. The keys are the tweets ids and values are dicts that contain:
        'sentiment' : the sentiment information as being analysed from the text, (positive, nuetral or negative)
        'sentiment_distribution' : a list that has the distribution of the three sentiments (the highest would be at the index of the selected sentiment)
    """
    headers = {'content-type': 'application/json; charset=utf-8'}
    url_sent = ApplicationConfig.SA_URL
    data = json.dumps(tweets, ensure_ascii=False)
    rs = -1
    try:
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print('Send to SA; Current Time =', current_time)
        response = requests.post(url=url_sent, headers = headers , data=data.encode('utf-8'))
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print('SA finished; Current Time =', current_time)
        rs = response.status_code
    except Exception:
        pass
        
    if rs != 200:
        print('Sentiment analyzer not working!.. Error code: ' + str(rs))
        logger.warning(f'[get_sentiments]: Sentiment analyzer not working!.. Error code: {str(rs)}')
        time.sleep(3)
        # only update if the sentiment api running and accessible.
        return None
    return json.loads(response.content)
    
    
def get_language(tweet_text):
    """function to extract the language of the passed string.
    It is based on fasttext language identification and uses the libraries (fasttext, re) in python.
    Proceudre:
        1- remove urls and mentions
        2- remove the numbers
        3- predict the language
        4- in case of errors, return english with 0 confidence.
    Args:
        tweet_text (str): The string that you need to find its language.

    Returns:
        language (str): The string that contains the identified language. examples: 'english' or 'spanish'
    """
    try:
        tweet_text = re.sub('http[s]:[^\b \n\t]+',' ',tweet_text)
        tweet_text = re.sub('@[^\b \n\t]+',' ',tweet_text)
        tweet_text = re.sub('[0-9]+',' ',tweet_text)
        tweet_text = re.sub('[\n\t ]+',' ',tweet_text).strip()
        if len(tweet_text.split(' ')) >= 1 and len(tweet_text) > 1:
            lang = detect(text=tweet_text, low_memory=False)
            if len(lang) >= 1:
                language = str(lang['lang'])
                return LANGUAGE_DICT[language] if language in LANGUAGE_DICT.keys() else language
            else:
                return 'NonText'
        else:
            return 'NonText'
    except Exception as exp:
        print(exp)
        time.sleep(1)
        return 'lang' #if exception occurred, set language to lang. (traceable for future works)

def get_urls_from_object(tweet_obj):
    """Extract urls from a tweet object

    Args:
        tweet_obj (dict): A dictionary that is the tweet object, extended_entities or extended_tweet

    Returns:
        list: list of urls that are extracted from the tweet.
    """
    url_list = []
    if "entities" in tweet_obj.keys():
        if "urls" in tweet_obj["entities"].keys():
            for x in tweet_obj["entities"]["urls"]:
                try:
                    url_list.append(x["expanded_url"]  if "expanded_url" in x.keys() else x["url"])
                except Exception:
                    pass
    return url_list


def extractMediaContentsFromDict(items=None, media_dict=dict()):
    """Extract media objects from a file
    Args:
        file (str): The path of the file.
        media_dict (dict): A dictionary that is the media objects.
    Returns:
        media_dict (dict): The updated dictionary that is the media objects.
    """
    if items:
        for item in items:
            try:
                if item['media_key'] not in media_dict.keys():
                    if 'url' in item.keys():
                        media_dict[item['media_key']] = item
            except Exception as exp:
                handleException(exp,item,__name__)
    return media_dict

def getMediaFromObject(media_dict, media_keys):
    """Extract urls from a tweet object
    Args:
        media_keys (dict): A dictionary that holds the media_keys
    Returns:
        list: list of the media urls that are extracted from the tweet.
    """
    media_list = []
    try:
        for item in media_keys:
            if item in media_dict.keys():
                item_ = media_dict[item]
                if "url" in item_.keys():
                    media_list.append(item_['url'])
    except Exception as exp:
        pass
    return media_list

def getPlatform(source = '<PLT_1>'):
    """A function to extract the platform from a source string.
    Args:
        source (str, optional): source string that is usually contains the platform that is used to post the tweet. Defaults to '<PLT_1>'.
    Returns:
        str: the platform if found, otherwise the stamp PLT_1. This stamp is used for any further updates.
    """
    platform = ''
    try:
        platform = re.sub('[<>]', '\t', source).split('\t')[2]
        platform = platform.replace('Twitter for','').replace('Twitter','')
    except:
        platform = ''
    return platform.strip()


        

def get_location(tweets):
    """A function to access location service.

    Args:
        tweets (dict): A dictionary of the tweets object. It should have the following keys:
        1) 'id': tweet id, 
        2) 'user': the user object as exists in the tweet object,
        3) 'geo': the geo field from the tweet,
        4) 'coordinates': the coordinates field from the tweet, 
        5) 'place': the place field from the tweet, 
        6) 'language': the detected language of the tweet.

    Returns:
        dict: A dictionary that hold the location information as retrived from location service. The keys are the tweets ids and values are dicts that contain
        'user' : the location information from user object
        'tweet' : the location information from the tweet object (location_gps)
        'language' (optional): the location as extracted from the tweets' language
    """
    url1 = ApplicationConfig.LOCATION_URL
    data = json.dumps(tweets,ensure_ascii=False)
    headers = {'content-type': 'application/json; charset=utf-8'}
    # sending get request and saving the response as response object
    rs = -1
    trials = 1
    while (rs != 200 and trials <= 3):
        try:
            response = requests.post(url=url1, data=data.encode('utf-8'), headers=headers)
            rs = response.status_code
        except Exception as exp:
            print(exp)
            rs = -1
        finally:
            trials += 1
    if rs != 200:
        logger.warning(f'[get_location]: Location service not found. Error code: ' + str(rs))
        # return None, to only update if the location api running and accessible.
        return None
    return json.loads(response.content)

def extract_raw_responses(json_response, filename = None, OUTPUT_FOLDER=None):
    try:
        tweets = None
        users = None
        includes = None
        places = None
        media = None
        poll = None
        matching_rules = None

        if 'matching_rules' in json_response.keys():
            matching_rules = [x['tag'] for x in json_response['matching_rules']]

        tweets = json_response['data'] if 'data' in json_response.keys() else None
        if tweets:
            if matching_rules:
                tweets['matching_rules'] = list(set(tweets['matching_rules'] + matching_rules)) if 'matching_rules' in tweets.keys() else list(set(matching_rules))

        if 'includes' in json_response.keys():
            users = json_response['includes']['users'] if 'users' in json_response['includes'].keys() else None
            includes = json_response['includes']['tweets'] if 'tweets' in json_response['includes'].keys() else None
            if includes:
                for item in includes:
                    if matching_rules:
                        item['matching_rules'] = list(set(item['matching_rules'] + matching_rules)) if 'matching_rules' in item.keys() else list(set(matching_rules))

            places = json_response['includes']['places'] if 'places' in json_response['includes'].keys() else None
            media = json_response['includes']['media'] if 'media' in json_response['includes'].keys() else None
            poll = json_response['includes']['poll'] if 'poll' in json_response['includes'].keys() else None


        if OUTPUT_FOLDER and filename:

            writeDataToFile(tweets, 'tweets_'+filename, OUTPUT_FOLDER)
            writeDataToFile(users, 'users_'+filename, OUTPUT_FOLDER)
            writeDataToFile(includes, 'includes_'+filename, OUTPUT_FOLDER)
            writeDataToFile(places, 'places_'+filename, OUTPUT_FOLDER)
            writeDataToFile(media, 'media_'+filename, OUTPUT_FOLDER)
            writeDataToFile(poll, 'poll_'+filename, OUTPUT_FOLDER)
        else:
            return tweets, users, includes, places, media, poll

    except Exception as exp:
        handleException(exp, object_=json_response, func_=f'\n{__name__}')

def getEmotion(text = ''):
    """
    -- Not implemented yet --
    A function to extract the emotion from a text string.
    Args:
        text (str, optional): text string of the tweet. Defaults to ''.
    Returns:
        str: the emotion.
    """
    return ''

def extractResponseContentsFromDict(items=None, objects_dict=dict()):
    if items:
        for item in items:
            try:
                if 'id' in item.keys():
                    if item['id'] not in objects_dict.keys():
                        objects_dict[item['id']] = item
            except Exception as exp:
                handleException(exp,item,__name__)
    return objects_dict

def getEmojis(text):
    try:
        emojis = emoji.distinct_emoji_list(text.encode('utf-16', 'surrogatepass').decode('utf-16'))
    except Exception as exp:
        emojis = emoji.distinct_emoji_list(text)
    finally:
        return emojis
    
def getCleanedText(text):
    #remove mentions, hashtags and urls
    t = ' '.join([x for x in tokenizer.tokenize(text) if not x.startswith('@') and not x.startswith('#') and not x.startswith('http')])
    return re.sub("[•!?;,/’‘&%'\"\t\n\.....； ]+"," ", t)

def getCleanedTextList(text):
    try:
        return getCleanedText(text).split(' ')
    except Exception as exp:
        return ""

def handleException(exp, object_='Unknown', func_= 'Unknown'):
    print(f'Error {exp}\n')
    exception_type, exception_object, exception_traceback = sys.exc_info()
    line_number = exception_traceback.tb_lineno
    
    print(f"------------------------------------------------\nException type: {exception_type}\n \
        Line number: {line_number}.\nexception_object: {exception_object}\n \
            Exception message : {exp}\nObject: {object_}\nFunction: {func_}.\
                \n================================================")
                
def getTweetContent(object_, original, users_dict, places_dict, media_dict):
    tweet_ = dict()

    author_id = object_['author_id']
    public_metrics = object_['public_metrics']
    author_location = 'not_available'
    verified = ''
    protected = ''
    user_name = ''
    user_screen_name = ''
    users_description = ''
    users_followers_count = None
    users_friends_count = None
    place_country = ''
    place_full_name = ''
    location_gps = None
    if 'geo' in object_.keys():
        if 'place_id' in object_['geo'].keys():
            place_id = object_['geo']['place_id']
            if place_id in places_dict.keys():
                if 'full_name' in places_dict[place_id].keys():
                    place_full_name = places_dict[place_id]['full_name']
                if 'country' in places_dict[place_id].keys():
                    place_country = places_dict[place_id]['country']

    if place_full_name == "" and place_country == "":
        location_gps = 'not_available'

    if  author_id in users_dict.keys():
        user_obj =  users_dict[author_id]
        if 'location' in user_obj.keys():
            author_location = user_obj['location']
        if 'verified' in user_obj.keys():
            verified = user_obj['verified']
        if 'protected' in user_obj.keys():
            protected = user_obj['protected']
        if 'screen_name' in user_obj.keys():
            user_screen_name = user_obj['screen_name']
        elif 'username' in user_obj.keys():
            user_screen_name = user_obj['username']
        if 'name' in user_obj.keys():
            user_name = user_obj['name']
        if 'description' in user_obj.keys():
            users_description = user_obj['description']
        if 'public_metrics' in user_obj.keys():
            if 'followers_count' in user_obj['public_metrics'].keys():
                users_followers_count = user_obj['public_metrics']['followers_count']
        if 'public_metrics' in user_obj.keys():
            if 'following_count' in user_obj['public_metrics'].keys():
                users_friends_count = user_obj['public_metrics']['following_count']

    media_keys = []
    if "attachments" in object_.keys():
        if "media_keys" in object_["attachments"].keys():
            media_keys = getMediaFromObject(media_dict,object_["attachments"]["media_keys"])

    urls = get_urls_from_object(object_)
    full_text = object_['text'] if 'text' in object_.keys() else object_['full_text'] if 'full_text' in object_.keys() else ''
    tweet_ = {'id':object_['id'],
              'created_at':time.strftime('%Y-%m-%dT%H:%M:%SZ', time.strptime(object_['created_at'],'%Y-%m-%dT%H:%M:%S.%fZ')),
              'created_at_days':time.strftime('%Y-%m-%d', time.strptime(object_['created_at'],'%Y-%m-%dT%H:%M:%S.%fZ')),
              'created_at_months':time.strftime('%Y-%m', time.strptime(object_['created_at'],'%Y-%m-%dT%H:%M:%S.%fZ')),
              'created_at_years':time.strftime('%Y', time.strptime(object_['created_at'],'%Y-%m-%dT%H:%M:%S.%fZ')),
              'emotion': getEmotion(full_text),
              'favorite_count': public_metrics['like_count'],
              'full_text': full_text,
              'hashtags':[x.replace('#','') for x in tweet_tokenizer.tokenize(full_text) if x.startswith('#')],
              'mentions':[x.replace('@','') for x in tweet_tokenizer.tokenize(full_text) if x.startswith('@')],
              'language_twitter': LANGUAGE_DICT[object_['lang']] if object_['lang'] in LANGUAGE_DICT.keys() else object_['lang'],
              'language': get_language(full_text),
              'possibly_sensitive': object_['possibly_sensitive'],
              'place_country': place_country,
              'place_full_name': place_full_name,
              'user_id':author_id,
              'location_gps': location_gps,
              'user_location_original': author_location,
              'media': media_keys,
              'platform': getPlatform(object_['source']) if 'source' in object_.keys() else getPlatform(),
              'original':original,
              'quote_count': public_metrics['quote_count'],
              'retweet_count': public_metrics['retweet_count'],
              'reply_count': public_metrics['reply_count'],
              'urls': urls,
              'verified': verified,
              'protected': protected,
              'conversation_id': object_['conversation_id'] if 'conversation_id' in object_.keys() else None,
              'user_screen_name': user_screen_name,
              'user_name': user_name,
              'users_description': users_description,
              'users_followers_count': users_followers_count,
              'users_friends_count': users_friends_count,
              'matchingRule': object_['matching_rules'] if 'matching_rules' in object_.keys() else None,
              'emojis': getEmojis(full_text),
              'text' : getCleanedText(full_text),
              'processed_tokens':  getCleanedTextList(full_text),
              'processed_desc_tokens': getCleanedTextList(users_description),
             }

    return tweet_


def extractTweetsFromDict(object_, tweets_dict = dict(), original = False, users_dict = dict(), places_dict = dict(), retweets_dict = dict(), replies_dict = dict(), quotes_dict = dict(), media_dict = dict()):
    if object_:
        if type(object_) == list:
            if len(object_) == 1:
                object_ = object_[0]
            else:
                try:
                    items = object_.copy()
                    for object_ in items:
                        if 'referenced_tweets' in object_.keys():
                            for referenced_tweet in object_['referenced_tweets']:
                                if referenced_tweet['type'] == 'retweeted':
                                    author_id = object_['author_id']
                                    if referenced_tweet['id'] in retweets_dict.keys():
                                        if object_['id'] not in retweets_dict[referenced_tweet['id']].keys():
                                            if author_id in users_dict.keys():
                                                user_obj = users_dict[author_id]
                                                if 'screen_name' in user_obj.keys():
                                                    retweets_dict[referenced_tweet['id']][object_['id']] = {'user_id' : author_id, 'user_screen_name': user_obj['screen_name'], 'user_name': user_obj['name'], 'created_at':time.strftime('%Y-%m-%d', time.strptime(object_['created_at'],'%Y-%m-%dT%H:%M:%S.%fZ'))}
                                                else:
                                                    retweets_dict[referenced_tweet['id']][object_['id']] = {'user_id' : author_id, 'user_screen_name': user_obj['username'], 'user_name': user_obj['name'], 'created_at':time.strftime('%Y-%m-%d', time.strptime(object_['created_at'],'%Y-%m-%dT%H:%M:%S.%fZ'))}
                                                if 'location' in user_obj.keys():
                                                    retweets_dict[referenced_tweet['id']][object_['id']]['author_location'] = user_obj['location']
                                            else:
                                                retweets_dict[referenced_tweet['id']][object_['id']] = {'user_id' : author_id, 'user_screen_name': None, 'created_at':time.strftime('%Y-%m-%d', time.strptime(object_['created_at'],'%Y-%m-%dT%H:%M:%S.%fZ'))}
                                    else:
                                        if author_id in users_dict.keys():
                                            user_obj = users_dict[author_id]
                                            try:
                                                if 'screen_name' in user_obj.keys():
                                                    retweets_dict[referenced_tweet['id']] = {object_['id']: {'user_id' : author_id, 'user_screen_name': user_obj['screen_name'], 'user_name': user_obj['name'], 'created_at':time.strftime('%Y-%m-%d', time.strptime(object_['created_at'],'%Y-%m-%dT%H:%M:%S.%fZ'))}}
                                                else:
                                                    retweets_dict[referenced_tweet['id']] = {object_['id']: {'user_id' : author_id, 'user_screen_name': user_obj['username'], 'user_name': user_obj['name'], 'created_at':time.strftime('%Y-%m-%d', time.strptime(object_['created_at'],'%Y-%m-%dT%H:%M:%S.%fZ'))}}
                                                if 'location' in user_obj.keys():
                                                    retweets_dict[referenced_tweet['id']][object_['id']]['author_location'] = user_obj['location']
                                            except Exception as exp:
                                                handleException(exp,object_,f'{__name__} 4')
                                        else:
                                            retweets_dict[referenced_tweet['id']] = {object_['id']: {'user_id' : author_id, 'user_screen_name': None}}

                                if referenced_tweet['type'] == 'replied_to':
                                    if referenced_tweet['id'] in replies_dict.keys():
                                        if object_['id'] not in replies_dict[referenced_tweet['id']].keys():
                                            replies_dict[referenced_tweet['id']][object_['id']] = getTweetContent(object_, original, users_dict, places_dict, media_dict)
                                    else:
                                        replies_dict[referenced_tweet['id']] = {object_['id']: getTweetContent(object_, original, users_dict, places_dict, media_dict)}
                                    replies_dict[referenced_tweet['id']][object_['id']]['in_reply_to_id'] = referenced_tweet['id']

                                if referenced_tweet['type'] == 'quoted':
                                    if referenced_tweet['id'] in quotes_dict.keys():
                                        if object_['id'] not in quotes_dict[referenced_tweet['id']].keys():
                                            quotes_dict[referenced_tweet['id']][object_['id']] = getTweetContent(object_, original, users_dict, places_dict, media_dict)
                                    else:
                                        quotes_dict[referenced_tweet['id']] = {object_['id']: getTweetContent(object_, original, users_dict, places_dict, media_dict)}
                                    quotes_dict[referenced_tweet['id']][object_['id']]['quotation_id'] = referenced_tweet['id']
                        else:
                            if object_['id'] not in tweets_dict.keys():
                                tweets_dict[object_['id']] = getTweetContent(object_, original, users_dict, places_dict, media_dict)
                            else:
                                try:
                                    if 'retweet_count' in tweets_dict[object_['id']].keys() and 'retweet_count' in object_:
                                        tweets_dict[object_['id']]['retweet_count']= max(tweets_dict[object_['id']]['retweet_count'], object_['retweet_count'])
                                    if 'reply_count' in tweets_dict[object_['id']].keys() and 'reply_count' in object_:
                                        tweets_dict[object_['id']]['reply_count']= max(tweets_dict[object_['id']]['reply_count'], object_['reply_count'])
                                    if 'favorite_count' in tweets_dict[object_['id']].keys() and 'like_count' in object_:
                                        tweets_dict[object_['id']]['favorite_count']= max(tweets_dict[object_['id']]['like_count'], object_['like_count'])
                                    if 'quote_count' in tweets_dict[object_['id']].keys() and 'quote_count' in object_:
                                        tweets_dict[object_['id']]['quote_count']= max(tweets_dict[object_['id']]['quote_count'], object_['quote_count'])
                                except Exception as exp:
                                    handleException(exp,tweets_dict[object_['id']],f'{__name__} 5')
                except Exception as exp3:
                    handleException(exp3,object_,func_=f'{__name__}')
                return tweets_dict, retweets_dict, replies_dict, quotes_dict
        try:
            if 'referenced_tweets' in object_.keys():
                for referenced_tweet in object_['referenced_tweets']:
                    if referenced_tweet['type'] == 'retweeted':
                        author_id = object_['author_id']
                        if referenced_tweet['id'] in retweets_dict.keys():
                            if object_['id'] not in retweets_dict[referenced_tweet['id']].keys():
                                if author_id in users_dict.keys():
                                    user_obj = users_dict[author_id]
                                    if 'screen_name' in user_obj.keys():
                                        retweets_dict[referenced_tweet['id']][object_['id']] = {'user_id' : author_id, 'user_screen_name': user_obj['screen_name'], 'user_name': user_obj['name'], 'created_at':time.strftime('%Y-%m-%d', time.strptime(object_['created_at'],'%Y-%m-%dT%H:%M:%S.%fZ'))}
                                    else:
                                        retweets_dict[referenced_tweet['id']][object_['id']] = {'user_id' : author_id, 'user_screen_name': user_obj['username'], 'user_name': user_obj['name'], 'created_at':time.strftime('%Y-%m-%d', time.strptime(object_['created_at'],'%Y-%m-%dT%H:%M:%S.%fZ'))}
                                    if 'location' in user_obj.keys():
                                        retweets_dict[referenced_tweet['id']][object_['id']]['author_location'] = user_obj['location']
                                else:
                                    retweets_dict[referenced_tweet['id']][object_['id']] = {'user_id' : author_id, 'user_screen_name': None, 'created_at':time.strftime('%Y-%m-%d', time.strptime(object_['created_at'],'%Y-%m-%dT%H:%M:%S.%fZ'))}
                        else:
                            if author_id in users_dict.keys():
                                user_obj = users_dict[author_id]
                                try:
                                    if 'screen_name' in user_obj.keys():
                                        retweets_dict[referenced_tweet['id']] = {object_['id']: {'user_id' : author_id, 'user_screen_name': user_obj['screen_name'], 'user_name': user_obj['name'], 'created_at':time.strftime('%Y-%m-%d', time.strptime(object_['created_at'],'%Y-%m-%dT%H:%M:%S.%fZ'))}}
                                    else:
                                        retweets_dict[referenced_tweet['id']] = {object_['id']: {'user_id' : author_id, 'user_screen_name': user_obj['username'], 'user_name': user_obj['name'], 'created_at':time.strftime('%Y-%m-%d', time.strptime(object_['created_at'],'%Y-%m-%dT%H:%M:%S.%fZ'))}}
                                    if 'location' in user_obj.keys():
                                        retweets_dict[referenced_tweet['id']][object_['id']]['author_location'] = user_obj['location']
                                except Exception as exp:
                                    handleException(exp,object_,f'{__name__} 4')
                            else:
                                retweets_dict[referenced_tweet['id']] = {object_['id']: {'user_id' : author_id, 'user_screen_name': None}}

                    if referenced_tweet['type'] == 'replied_to':
                        if referenced_tweet['id'] in replies_dict.keys():
                            if object_['id'] not in replies_dict[referenced_tweet['id']].keys():
                                replies_dict[referenced_tweet['id']][object_['id']] = getTweetContent(object_, original, users_dict, places_dict, media_dict)
                        else:
                            replies_dict[referenced_tweet['id']] = {object_['id']: getTweetContent(object_, original, users_dict, places_dict, media_dict)}
                        replies_dict[referenced_tweet['id']][object_['id']]['in_reply_to_id'] = referenced_tweet['id']

                    if referenced_tweet['type'] == 'quoted':
                        if referenced_tweet['id'] in quotes_dict.keys():
                            if object_['id'] not in quotes_dict[referenced_tweet['id']].keys():
                                quotes_dict[referenced_tweet['id']][object_['id']] = getTweetContent(object_, original, users_dict, places_dict, media_dict)
                        else:
                            quotes_dict[referenced_tweet['id']] = {object_['id']: getTweetContent(object_, original, users_dict, places_dict, media_dict)}
                        quotes_dict[referenced_tweet['id']][object_['id']]['quotation_id'] = referenced_tweet['id']
            else:
                if object_['id'] not in tweets_dict.keys():
                    tweets_dict[object_['id']] = getTweetContent(object_, original, users_dict, places_dict, media_dict)
                else:
                    try:
                        if 'retweet_count' in tweets_dict[object_['id']].keys() and 'retweet_count' in object_:
                            tweets_dict[object_['id']]['retweet_count']= max(tweets_dict[object_['id']]['retweet_count'], object_['retweet_count'])
                        if 'reply_count' in tweets_dict[object_['id']].keys() and 'reply_count' in object_:
                            tweets_dict[object_['id']]['reply_count']= max(tweets_dict[object_['id']]['reply_count'], object_['reply_count'])
                        if 'favorite_count' in tweets_dict[object_['id']].keys() and 'like_count' in object_:
                            tweets_dict[object_['id']]['favorite_count']= max(tweets_dict[object_['id']]['like_count'], object_['like_count'])
                        if 'quote_count' in tweets_dict[object_['id']].keys() and 'quote_count' in object_:
                            tweets_dict[object_['id']]['quote_count']= max(tweets_dict[object_['id']]['quote_count'], object_['quote_count'])
                    except Exception as exp:
                        handleException(exp,tweets_dict[object_['id']],f'{__name__} 5')
        except Exception as exp3:
            handleException(exp3,object_,func_=f'{__name__}')
    return tweets_dict, retweets_dict, replies_dict, quotes_dict


# Creating the logger object
logger = create_logger('util', file='util')

