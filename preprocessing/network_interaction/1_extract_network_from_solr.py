#!/usr/bin/env python3
"""
Python script for extracting the network interaction from Apache Solr.

This script interacts with solr_class with the function get_network_interaction
to retrieve the network of users as a dict object that holds the target objects as keys,
and the values are dicts of keys (sources) and values (weights)
It writes the source, target, weight table into a csv file.

Usage:
    python 1_extract_network_from_solr.py -c core_name

Requirements:
    - Apache Solr instance running and accessible.
    - the data_updater folder that has the solr_class.py inside the parent folder.
    - Python library 'pysolr' installed (install via 'pip install pysolr')
    - Python library 'networkx' installed (install via 'pip install networkx')
    - Python library 'pandas' installed (install via 'pip install pandas')
"""
import pandas as pd
import networkx as nx
import os
import sys
MAX_EDGES = 500000
DATA_DIR = "./data"
DATA_FILE = "df_data"
try:
    source_dir = os.path.abspath(os.path.join('../data_updater'))
    sys.path.append(source_dir)
except Exception as exp:
    print_this("Solr Class Not Found, please make sure the data_updater in the parent folder and it has the correct solr_class.py file!")
    sys.exit(-1)
from solr_class import *


if __name__== "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--core', help="please specify core", default=None)

    args = parser.parse_args()
    core = args.core

    solr = SolrClass({})
    if core != None:
        users_edges, hits = solr.get_network_interaction(core)

        # convert the dict to records.
        records = [{'source': source, 'target': target, 'weight': weight}
                   for target, edges in users_edges.items()
                   for source, weight in edges.items()]

        # convert the records to DataFrame
        data_df = pd.DataFrame.from_records(records)

        # neglect the self loop nodes:
        data_df = data_df[data_df['source'] != data_df['target']]

        # Calculate the frequencies of each node (account):
        combined_series = pd.concat([data_df['source'], data_df['target']])
        combined_freq = combined_series.value_counts()

        # Add frequency counts to the DataFrame:
        data_df['source_freq'] = data_df['source'].map(combined_freq).fillna(0).astype(int)
        data_df['target_freq'] = data_df['target'].map(combined_freq).fillna(0).astype(int)

        # Calculate combined frequency:
        data_df['freq'] = data_df['source_freq'] + data_df['target_freq']

        # Calculate the pagerank:
        G = nx.from_pandas_edgelist(data_df, 'source', 'target', ['weight'], create_using=nx.DiGraph())
        pagerank = nx.pagerank(G)
        data_df['pagerank'] = data_df.target.apply(lambda x : pagerank[x])
        
        # limiting the network to the maximum number of edges (required for resource constraints)
        threshold  = 1
        while len(data_df) > MAX_EDGES:
            if len(data_df[data_df['pagerank']> data_df.pagerank.min()]) >= len(data_df[data_df['freq']>threshold]):
                data_df = data_df[data_df['pagerank']> data_df.pagerank.min()]
            else:
                threshold += 1
                data_df= data_df[data_df['freq']>=threshold]

        # Write out the dataframe to csv file.
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        output_file = f'{DATA_DIR}/{DATA_FILE}_{core}.csv'
        data_df[['source','target','weight']].to_csv(output_file, index=False)
        print_this(f"Data written to file {output_file}")
    else:
        print_this("Please identify the core. You can run the code with command: python 1_extract_network_from_solr.py -c new_core")