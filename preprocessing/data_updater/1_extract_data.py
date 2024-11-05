#!/usr/bin/env python3

"""
Python script for extract the information from raw tweets stored in files within the located folder.

This script reads tweets from a file and imports them into combined dict.
It assumes that the tweets are stored in a JSON format in which each tweet is in a separate line.

Usage:
    python 1_extract_data.py -s source_folder_path -o output_folder_path

Requirements:
"""
import os
import json
import shutil
import tarfile
from os import listdir
import datetime
from os.path import isfile, join
from urllib.request import urlopen
import argparse
from util import *


if __name__== "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--data_path', help="The path to the folder that the raw tweets files located in, in the files, each tweet in expected to be in a separate line.", default=None)
    parser.add_argument('-o', '--output_path', help="The path to the processed tweets to write the data to.", default=None)

    args = parser.parse_args()
    data_path = args.data_path

    OUTPUT_FOLDER = args.output_path
    if data_path == None:
        print("Please enter the folder of which the source data located in.")
        sys.exit(-1)
    
    if data_path.endswith("/"):
        data_path = data_path[:-1]
    
    if OUTPUT_FOLDER == None:
            OUTPUT_FOLDER = f"{data_path}_processed"
    print(f"The processed tweets will be written to the folder {OUTPUT_FOLDER}")
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)



    
    users_files = []
    day = datetime.datetime.now()
    limit = day.strftime('%Y_%m_%d')
    limit_day = day.strftime('%Y_%m_%d')

    import glob

    workfiles = list(set([f for f in glob.glob(f"{data_path}/**/*", recursive=True) if isfile(f) and not f.endswith('.gz') and not f.endswith('.bz2')]))
    print(f'work_files: {workfiles}')

    for workFile in sorted(workfiles):
        print(workFile)
        retweets_dict = dict()
        replies_dict = dict()
        quotes_dict = dict()
        tweets_dict = dict()
        users_dict = dict()
        media_dict = dict()
        places_dict = dict()
        lines = 0
        tweets = []
        if os.path.exists(workFile):
            with open(workFile, 'r' , encoding='utf-8') as fin:
                for line in fin:
                    try:
                        objects = json.loads(line.strip())
                    except Exception as exp:
                        objects = None
                    if objects != None:
                        lines += 1
                        tweets, users, includes, places, media, poll = extract_raw_responses(objects)
                        places_dict = extractResponseContentsFromDict(places, places_dict)
                        media_dict = extractMediaContentsFromDict(media, media_dict)
                        users_dict = extractResponseContentsFromDict(users, users_dict)
                        if type(includes) == list:
                            for obj_ in includes:
                                tweets_dict, retweets_dict, replies_dict, quotes_dict = extractTweetsFromDict(obj_, tweets_dict, False, users_dict, places_dict, retweets_dict, replies_dict, quotes_dict, media_dict)
                        else:
                            tweets_dict, retweets_dict, replies_dict, quotes_dict = extractTweetsFromDict(includes, tweets_dict, False, users_dict, places_dict, retweets_dict, replies_dict, quotes_dict, media_dict)
                        if type(tweets) == list:
                            for obj_ in tweets:
                                tweets_dict, retweets_dict, replies_dict, quotes_dict = extractTweetsFromDict(obj_, tweets_dict, True, users_dict, places_dict, retweets_dict, replies_dict, quotes_dict, media_dict)
                        else:
                            tweets_dict, retweets_dict, replies_dict, quotes_dict = extractTweetsFromDict(tweets, tweets_dict, True, users_dict, places_dict, retweets_dict, replies_dict, quotes_dict, media_dict)


            combined_dict = tweets_dict.copy()

            for k in replies_dict.keys():
                for j in replies_dict[k].keys():
                    if j not in combined_dict.keys():
                        combined_dict[j] = replies_dict[k][j]
            for k in quotes_dict.keys():
                for j in quotes_dict[k].keys():
                    if j not in combined_dict.keys():
                        combined_dict[j] = quotes_dict[k][j]

            for k in replies_dict.keys():
                for j in replies_dict[k].keys():
                    if k in combined_dict.keys():
                        if 'replies_tweets' not in combined_dict[k].keys():
                            combined_dict[k]['replies_tweets'] = [j]
                        else:
                            if j not in combined_dict[k]['replies_tweets']:
                                combined_dict[k]['replies_tweets'].append(j)

                        replies_times = f"{replies_dict[k][j]['user_screen_name']} {replies_dict[k][j]['created_at']}"
                        if 'replies_times' not in combined_dict[k].keys():
                            combined_dict[k]['replies_times'] = [replies_times]
                        if replies_times not in combined_dict[k]['replies_times']:
                            combined_dict[k]['replies_times'].append(replies_times)

            for k in retweets_dict.keys():
                for j in retweets_dict[k].keys():
                    if k in combined_dict.keys():
                        if 'retweeters' not in combined_dict[k].keys():
                            combined_dict[k]['retweeters'] = [retweets_dict[k][j]['user_screen_name']]
                        else:
                            if retweets_dict[k][j]['user_screen_name'] not in combined_dict[k]['retweeters']:
                                combined_dict[k]['retweeters'].append(retweets_dict[k][j]['user_screen_name'])
                        if 'created_at_days' in retweets_dict[k][j].keys():
                            retweet_times = f"{retweets_dict[k][j]['user_screen_name']} {retweets_dict[k][j]['created_at_days']}"
                        elif 'created_at' in retweets_dict[k][j].keys():
                            retweet_times = f"{retweets_dict[k][j]['user_screen_name']} {retweets_dict[k][j]['created_at'][0:10]}"
                        else:
                            retweet_times = f"{retweets_dict[k][j]['user_id']}"

                        if 'retweet_times' not in combined_dict[k].keys():
                            combined_dict[k]['retweet_times'] = [retweet_times]
                        if retweet_times not in combined_dict[k]['retweet_times']:
                            combined_dict[k]['retweet_times'].append(retweet_times)

            for k in quotes_dict.keys():
                for j in quotes_dict[k].keys():
                    if k in combined_dict.keys():
                        if 'quote_tweets' not in combined_dict[k].keys():
                            combined_dict[k]['quote_tweets'] = [j]
                        else:
                            if j not in combined_dict[k]['quote_tweets']:
                                combined_dict[k]['quote_tweets'].append(j)

                        if 'quoters' not in combined_dict[k].keys():
                            combined_dict[k]['quoters'] = [quotes_dict[k][j]['user_screen_name']]
                        else:
                            if quotes_dict[k][j]['user_screen_name'] not in combined_dict[k]['quoters']:
                                combined_dict[k]['quoters'].append(quotes_dict[k][j]['user_screen_name'])
                        if 'created_at_days' in quotes_dict[k][j].keys():
                            quote_times = f"{quotes_dict[k][j]['user_screen_name']} {quotes_dict[k][j]['created_at_days']}"
                        elif 'created_at' in quotes_dict[k][j].keys():
                            quote_times = f"{quotes_dict[k][j]['user_screen_name']} {quotes_dict[k][j]['created_at'][0:10]}"
                        else:
                            quote_times = f"{quotes_dict[k][j]['user_id']}"

                        if 'quote_times' not in combined_dict[k].keys():
                            combined_dict[k]['quote_times'] = [quote_times]

                        if quote_times not in combined_dict[k]['quote_times']:
                            combined_dict[k]['quote_times'].append(quote_times)


            outputFile = workFile.split("/")[-1] if len(workFile.split("/")) > 1 else "outputFile"


            with open(join(OUTPUT_FOLDER, outputFile), 'a+', encoding='utf-8') as fout:
                for k in combined_dict.keys():
                    fout.write(f"{json.dumps(combined_dict[k], ensure_ascii=False)}\n")
