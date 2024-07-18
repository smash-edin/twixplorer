#!/usr/bin/env python3
import os
import sys
import pandas as pd
import argparse
from extract_text_data import DATA_DIR, DATA_FILE


try:
    source_dir = os.path.abspath(os.path.join('../data_updater'))
    sys.path.append(source_dir)
except Exception as exp:
    print_this("Solr Class Not Found, please make sure the data_updater in the parent folder and it has the correct solr_class.py file!")
    sys.exit(-1)
from solr_class import *
from configs import ApplicationConfig

limit = 100000

def get_args():
    """ Defines hyper-parameters. """
    parser = argparse.ArgumentParser('Run NLI model on corpus')

    # Add data arguments
    parser = argparse.ArgumentParser('Update Embeddings in Solr')
    parser.add_argument('-c', '--core', help="The Solr core.", default=None)
    parser.add_argument('-s', '--input_file', help="The embeddings file.", default=f'{DATA_DIR}/{DATA_FILE}_w_embeddings_5d_2d.pkl',)

    args = parser.parse_args()
    return args

def get_embedding_from_file(fileName):
    try:
        df = pd.read_pickle(fileName)
        return df, True
    except Exception as exp:
        print_this(f"Error at loading data from file {fileName}")
        return None, False

if __name__== "__main__":

    # current version works only on retweeting interaction. preparing fields name in Solr
    network_label = 'retweet'
    network = 'retweet_times'

    # getting passed arguments
    args = get_args()
    core = args.core
    input_file = args.input_file

    nodes_networks, fileLoaded = get_embedding_from_file(input_file)
    if core == None:
            print("Please provide the Solr core. The command might be:\n python import_networks_to_solr.py -c new_core.\n")

    elif not fileLoaded:
        print("Input file does not loaded properlya. Check the existence of the file, and then enter the command:\n python import_networks_to_solr.py -c new_core -s edges_GRAPH.json.\n")
    elif core in ApplicationConfig.SOLR_CORES:
        dataSource = SolrClass({})

        nodes_networks.index = nodes_networks['id']

        nodes_networks_dict = nodes_networks[['id','embedding_5d','embedding_2d']].to_dict(orient="index")

        print(f"Saving {network} network to Solr")
        dataSource.add_items_to_solr(core, list(nodes_networks_dict.values()))
    else:
        print("Loading data file and accessing Solr core failed.")