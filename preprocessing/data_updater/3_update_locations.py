# -*- coding: utf-8 -*-

import datetime as dt
import requests
import time
import json
from util import get_location
import getpass
import sys
from configs import ApplicationConfig
from solr_class import *

status_file = '../.log/status_file_locations'

if __name__== "__main__":
	run = True
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('-c', '--core', help="please specify core", default=None)

	args = parser.parse_args()
	core = args.core

	solr = SolrClass({})
	if core != None:
	
		tweets_all, max_row = solr.get_no_location_items(core)

		tweets_list = []
		while len(tweets_all) > 0:
			tweets = tweets_all[0:10000]
			tweets_all = tweets_all[10000:]
			loc_dict = dict()
			for tweet in tweets:
				loc_dict[tweet['id']] = {'id': tweet['id'], 'user': {'location': tweet['user_location_original'] if 'user_location_original' in tweet.keys() else 'not_available'}, 'place': {'country': tweet['place_country'] if 'place_country' in tweet.keys() else 'not_available', 'place_full_name': tweet['place_full_name'] if 'place_full_name' in tweet.keys() else 'not_available'}}
			locations = get_location(loc_dict)

			# only update if the location api running and accessible.
			if locations != None:
				for k in locations.keys():
					tweets_list.append({'id': k, 'user_location': locations[k]['user'], 'location_gps': locations[k]['tweet']})

			solr.add_items_to_solr(core, tweets_list)
			if len(tweets_all) == 0:
				time.sleep(5) # wait Solr's soft commit
				tweets_all, max_row = solr.get_no_location_items(core)
		if max_row == 0:
			print("Updating locations finished.")
	else:
		print('Please make sure that command contains the core instance name.')
