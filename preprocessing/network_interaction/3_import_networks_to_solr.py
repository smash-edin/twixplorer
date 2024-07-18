#!/usr/bin/env python3
import os
import sys
try:
    source_dir = os.path.abspath(os.path.join('../data_updater'))
    sys.path.append(source_dir)
except Exception as exp:
    print_this("Solr Class Not Found, please make sure the data_updater in the parent folder and it has the correct solr_class.py file!")
    sys.exit(-1)
from solr_class import *
from configs import ApplicationConfig

limit = 100000


def get_netowrk_from_json_file(fileName):
    try:
        with open(fileName, "r", encoding="utf-8" ) as fin:
            lines = json.load(fin)
        nodes = dict()
        for node in lines['nodes']:
            if node['key'] not in nodes:
                nodes[node['key']] = f"{node['key']} {int(node['attributes']['modularity_class'])} {int(node['attributes']['size'])} ({node['attributes']['x']}, {node['attributes']['y']})"
        return nodes
    except Exception as exp:
        print_this(f"Error at loading data from file")

if __name__== "__main__":

    network_label = 'retweet'
    network = 'retweet_times'

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--core', help="The Solr core.", default=None)
    parser.add_argument('-s', '--input_file', help="The input file that holds the information of network computed by Java community detection module.", default=None)

    args = parser.parse_args()
    core = args.core
    input_file = args.input_file

    if input_file == None or core == None:
        print("Please select the input file and Solr core. The command might be:\n python import_networks_to_solr.py -c new_core -s edges_GRAPH.json.\n")
    else:
        dataSource = SolrClass({})
        nodes_networks = get_netowrk_from_json_file(input_file)

        if core in ApplicationConfig.SOLR_CORES:

            response = dataSource.get_network_interactions(solr_core=core, interaction=network)
            print(f"{network_label}_network_nodes")
            print(f"response keys : {response.keys()}")

            if response is not None:
                if "msg" in response.keys():
                    print(response['msg'])
                elif response['response']['numFound'] > 0:
                    tweets_packet = dict()
                    docs = response['response']['docs']
                    print(f"length of data: {len(docs)}")
                    for doc in docs:
                        print(doc['id'])
                        print(doc['retweet_times'])
                        new_list_of_network = list(set([doc['user_screen_name']] + [x.split(" ")[0] for x in doc['retweet_times']]))
                        new_list_of_network = [nodes_networks[k] for k in new_list_of_network if k in nodes_networks.keys()]
                        tweets_packet[doc['id']] = {'id': doc['id'], 'retweet_network_nodes': new_list_of_network, 'retweet_community':int(nodes_networks[doc['user_screen_name']].split(" ")[1] if doc['user_screen_name'] in nodes_networks else 0)}

                    print_this(list(tweets_packet.values())[0:2])

                    print(f"Saving {network} network to Solr")
                    dataSource.add_items_to_solr(core, list(tweets_packet.values()))


        print("Extracting Networks Done")