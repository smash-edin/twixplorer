import requests
import sys
sys.path.append('..')
from data_updater.configs import ApplicationConfig

def init_schema(url):
    scehma_contents = [
    {"name":"id","type":"string","stored":True,"multiValued":False,"required":True,"indexed":True},
    {"name":"created_at","type":"pdates","multiValued":False,"stored":True},
    {"name":"created_at_days","type":"string","multiValued":False,"stored":True,"omitNorms":True},
    {"name":"created_at_months","type":"string","multiValued":False,"stored":True,"omitNorms":True},
    {"name":"created_at_years","type":"string","multiValued":False,"stored":True,"omitNorms":True},
    {"name":"user_screen_name","type":"string","stored":True,"multiValued":False,"indexed":True},
    {"name":"user_name","type":"string","stored":True,"multiValued":False,"omitNorms":True,"indexed":True},
    {"name":"user_id","type":"string","stored":True,"multiValued":False,"omitNorms":True},
    {"name":"users_followers_count","type":"pint","stored":True,"multiValued":False,"omitNorms":True},
    {"name":"users_friends_count","type":"pint","stored":True,"multiValued":False,"omitNorms":True},
    {"name":"retweet_count","type":"pint","stored":True,"multiValued":False,"omitNorms":True},
    {"name":"favorite_count","type":"pint","stored":True,"multiValued":False,"omitNorms":True},
    {"name":"quote_count","type":"plong","stored":True,"multiValued":False,"omitNorms":True},
    {"name":"reply_count","type":"plong","stored":True,"multiValued":False,"omitNorms":True},
    {"name":"embedding_2d","type":"pfloat","uninvertible":True,"omitNorms":True,"multiValued":True,"indexed":True,"stored":True},
    {"name":"embedding_5d","type":"pfloat","uninvertible":True,"omitNorms":True,"multiValued":True,"indexed":True,"stored":True},
    {"name":"conversation_id","type":"string","stored":True,"multiValued":False,"omitNorms":True},
    {"name":"domains","type":"string","stored":True,"multiValued":True,"omitNorms":True},
    {"name":"emoji","type":"string","stored":True,"multiValued":True,"omitNorms":True},
    {"name":"emojis","type":"string","stored":True,"multiValued":True,"omitNorms":True},
    {"name":"emotion","type":"string","stored":True,"multiValued":False,"omitNorms":True},
    {"name":"emotion_distribution","type":"string","stored":True,"multiValued":True,"omitNorms":True},
    {"name":"features","type":"string","stored":True,"multiValued":True,"omitNorms":True},
    {"name":"full_text","type":"text_general","stored":True,"multiValued":False,"indexed":True},
    {"name":"hashtags","type":"text_general","stored":True,"multiValued":True,"indexed":True,"omitNorms":True},
    {"name":"mentions","type":"text_general","stored":True,"multiValued":True,"indexed":True,"omitNorms":True},
    {"name":"retweeters","type":"text_general","stored":True,"multiValued":True,"indexed":True,"omitNorms":True},
    {"name":"retweet_times","type":"string","stored":True,"multiValued":True,"indexed":True,"omitNorms":True},
    {"name":"users_description","type":"text_general","stored":True,"multiValued":False,"indexed":True},
    {"name":"users_location","type":"string","stored":True,"multiValued":False,"indexed":True},
    {"name":"in_reply_to_id","type":"string","stored":True,"multiValued":False,"omitNorms":True,"indexed":False,"uninvertible":False},
    {"name":"language","type":"string","stored":True,"multiValued":False,"indexed":True,"omitNorms":True},
    {"name":"language_twitter","type":"string","stored":True,"multiValued":False,"indexed":True,"omitNorms":True},
    {"name":"location_gps","type":"string","stored":True,"multiValued":False,"indexed":True,"omitNorms":True},
    {"name":"user_location","type":"string","stored":True,"multiValued":False,"indexed":True,"omitNorms":True},
    {"name":"user_location_original","type":"string","stored":True,"multiValued":False,"indexed":True,"omitNorms":True},
    {"name":"location_language","type":"string","stored":True,"multiValued":False,"indexed":True,"omitNorms":True},
    {"name":"matchingRule","type":"string","stored":True,"multiValued":True,"indexed":False,"omitNorms":True},
    {"name":"media","type":"string","stored":True,"multiValued":True,"indexed":False,"omitNorms":True},
    {"name":"original","type":"boolean","stored":True,"multiValued":False,"indexed":False,"omitNorms":True},
    {"name":"verified","type":"boolean","stored":True,"multiValued":False,"indexed":False,"omitNorms":True},
    {"name":"place_country","type":"string","stored":True,"multiValued":False,"indexed":True,"omitNorms":True},
    {"name":"place_full_name","type":"string","stored":True,"multiValued":False,"indexed":True,"omitNorms":True},
    {"name":"platform","type":"string","stored":True,"multiValued":False,"indexed":True},
    {"name":"possibly_sensitive","type":"boolean","stored":True,"multiValued":False,"indexed":False,"omitNorms":True},
    {"name":"processed_desc_tokens","type":"string","stored":True,"multiValued":True,"indexed":False,"omitNorms":True},
    {"name":"processed_tokens","type":"string","stored":True,"multiValued":True,"indexed":False,"omitNorms":True},
    {"name":"protected","type":"boolean","stored":True,"multiValued":False,"indexed":False,"omitNorms":True},
    {"name":"quotation_id","type":"string","stored":True,"multiValued":False,"indexed":False,"uninvertible":False,"omitNorms":True},
    {"name":"quote_times","type":"string","stored":True,"multiValued":True,"indexed":True,"omitNorms":True},
    {"name":"quote_tweets","type":"string","stored":True,"multiValued":True,"indexed":True,"omitNorms":True},
    {"name":"quoters","type":"string","stored":True,"multiValued":True,"indexed":True,"omitNorms":True},
    {"name":"replies_times","type":"string","stored":True,"multiValued":True,"indexed":True,"omitNorms":True},
    {"name":"replies_tweets","type":"string","stored":True,"multiValued":True,"indexed":True,"omitNorms":True},
    {"name":"reply_community","type":"pint","stored":True,"multiValued":False,"indexed":False,"omitNorms":True},
    {"name":"retweet_community","type":"pint","stored":True,"multiValued":False,"indexed":False,"omitNorms":True},
    {"name":"reply_network_nodes","type":"string","stored":True,"multiValued":True,"indexed":False,"omitNorms":True},
    {"name":"retweet_network_nodes","type":"string","stored":True,"multiValued":True,"indexed":False,"omitNorms":True},
    {"name":"sentiment","type":"string","stored":True,"multiValued":False,"indexed":False},
    {"name":"sentiment_distribution","type":"string","stored":True,"multiValued":True,"indexed":False},
    {"name":"topic","type":"string","stored":True,"multiValued":True,"indexed":False},
    {"name":"urls","type":"string","stored":True,"multiValued":True,"indexed":False}]
    headers = {'Content-type': 'application/json'}

    for item in scehma_contents:
        payload = {"add-field":item}
        r = requests.post(url, json=payload)
    return r


def add_core(core_name,path,url,port):
    import os
    r1 = os.system(f"{path}/bin/solr create -c {core_name}  -p {port}")
    url = f"{url}:{port}/solr/{core_name}/schema"
    r2 = init_schema(url)
    return (r1 == 0 and r2.status_code == 200)

def delete_core(core_name,path, port):
    import os
    r = os.system(f"{path}/bin/solr delete -c {core_name} -p {port}")
    return(r == 0)

def start_solr(path, port):
    import os
    r1 = os.system(f"{path}/bin/solr start -p {port}")

if __name__== "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--core', help="The Solr collection name", default=None)
    parser.add_argument('-d', '--command', help="please specify the command to be performed (add or delete core, or start solr).", default=None)

    args = parser.parse_args()
    cmd = args.command
    core = args.core

    if cmd == None:
        print("Please specify the command to be performed (add or delete core, or start solr).")
        exit(-1)

    elif cmd == "start":
        start_solr(ApplicationConfig.SOLR_PATH, ApplicationConfig.SOLR_PORT)
    elif core == None:
        print("Please specify the collection name (core).")
        exit(-1)
    else:
        if cmd == "add" or cmd == "create":
            if add_core(core, ApplicationConfig.SOLR_PATH, ApplicationConfig.SOLR_URL, ApplicationConfig.SOLR_PORT):
                print("The collection has been created successfully, please update the configs.py file accordingly.")
        elif cmd == "delete":
            if delete_core(core, ApplicationConfig.SOLR_PATH,ApplicationConfig.SOLR_PORT):
                print("The collection has been deleted successfully, please update the configs.py file accordingly.")
