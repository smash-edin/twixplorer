#!/usr/bin/env python3
import random
import argparse
import pandas as pd
from umap.parametric_umap import ParametricUMAP, load_ParametricUMAP
from extract_text_data import DATA_DIR, DATA_FILE
import sys

import gc
from tqdm import tqdm

def get_args():
    """ Defines hyper-parameters. """
    parser = argparse.ArgumentParser('Run NLI model on corpus')

    # Add data arguments
    parser.add_argument('--data', default=f'./{DATA_DIR}/{DATA_FILE}_w_embeddings.csv', help='Name of data file')
    parser.add_argument('--source-column', type=str, default='sbert_embedding', help='Name of column containing input embeddings')
    parser.add_argument('--training-size', type=int, default=200000, help='Number of examples to train reducer from')
    parser.add_argument('--out-file-reducer', default=None, help='Name of target file containing reducer')
    parser.add_argument('--out-file-data', default=None, help='Name of target file containing reduced embeddings')

    args = parser.parse_args()
    return args

def convert_string_to_array(text):
    try:
        return eval(",".join(text.replace("[ ", "[").replace(" ]", "]").split()))
    except Exception as exp:
        print("Data in the input file is not as expected. Please start the steps after cleaning the data folder.")
        sys.exit(-1)

if __name__ == '__main__':

    args = get_args()
    source_column = args.source_column
    data_path = args.data
    training_size = args.training_size

    if args.out_file_data is None:
        out_file_data = data_path.replace('.csv', '_5d.pkl')
    else:
        out_file_data = args.out_file_data
    print('Target file name for data:', out_file_data)

    if args.out_file_reducer is None:
        out_file_reducer = "./5d_embedder"
    else:
        out_file_reducer = args.out_file_reducer
    print('Target file name for reducer:', out_file_reducer)

    print("0. Loading data...")
    df = pd.read_csv(data_path)
    print(df.sample(5))
    if pd.api.types.is_string_dtype(df[source_column].dtype):
        df[source_column] = df[source_column].apply(convert_string_to_array)
    embeddings_all = df[source_column].to_list()

    print("1. Sampling training examples...")
    if len(embeddings_all) > training_size:
        train_embeddings = random.sample(embeddings_all, training_size)
    else:
        train_embeddings = embeddings_all
    print("\t...", len(train_embeddings), "embeddings used for training")

    print("2. Training 5d reducer...")
    embedder = ParametricUMAP(n_components=5).fit(train_embeddings)

    print("3. Saving 5d reducer...")
    embedder.save(out_file_reducer)

    print("4. Running model on all data...")
    reduced_embeddings_dfs_list = list()

    for start in tqdm(range(0, len(df), 1000)):
        end = start + 1000
        batch_df = df.iloc[start:end]

        if pd.api.types.is_string_dtype(batch_df[source_column].dtype):
            batch_df[source_column] = batch_df[source_column].apply(convert_string_to_array)

        batch_df['embedding_5d'] = embedder.transform(batch_df[source_column].to_list()).tolist()
        batch_df.drop(columns=[source_column], inplace=True)

        gc.collect()
        reduced_embeddings_dfs_list.append(batch_df)

    print("5. Saving 5d embeddings...")
    df_whole = pd.concat(reduced_embeddings_dfs_list)
    df_whole.to_pickle(out_file_data)

    print("Done!")