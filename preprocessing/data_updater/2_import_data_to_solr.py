#!/usr/bin/env python3
"""
Python script for importing tweets from a stored file into Apache Solr.

This script reads tweets from a file and imports them into an Apache Solr instance.
It assumes that the tweets are stored in a specific format within the file.

Usage:
    python 2_import_data_to_solr.py -c core_name -s source_file

Requirements:
    - Apache Solr instance running and accessible
    - Python library 'pysolr' installed (install via 'pip install pysolr')
"""

import json
from solr_class import *
import argparse

dataSource = SolrClass(filters={})

if __name__== "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', help="The tweets source file, each tweet in a separate line.", default=None)
    parser.add_argument('-c', '--core', help="The Solr core to write the data to.", default=None)

    args = parser.parse_args()
    core = args.core
    source = args.source

    if core != None and source != None:
        try:
            tweets = dict()
            with open(source, "r", encoding="utf-8") as fin:
                for t in fin:
                    t = json.loads(t)
                    tweets[t['id']] = t

                    if len(tweets) >= 100000:
                        dataSource.add_items_to_solr(core, list(tweets.values()))
                        tweets = dict()

            if len(tweets) > 0:
                dataSource.add_items_to_solr(core, list(tweets.values()))

        except Exception as exp:
            print(f"ERR: reading from file failed!\n{exp}")
    elif core == None:
        print("ERR: Please specify the Solr core!")
    else:
        print("ERR: Please specify the source file!")