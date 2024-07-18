import random
import argparse
import pandas as pd
from umap.parametric_umap import ParametricUMAP
from extract_text_data import DATA_DIR, DATA_FILE


def get_args():
    """ Defines hyper-parameters. """
    parser = argparse.ArgumentParser('Run NLI model on corpus')

    # Add data arguments
    parser.add_argument('--data', default=f'./{DATA_DIR}/{DATA_FILE}_w_embeddings_5d.pkl', help='Name of data file')
    parser.add_argument('--source-column', type=str, default='embedding_5d',
                        help='Name of column containing input embeddings')
    parser.add_argument('--training-size', type=int, default=200000, help='Number of examples to train reducer from')
    parser.add_argument('--out-file-reducer', default=None, help='Name of target file containing reducer')
    parser.add_argument('--out-file-data', default=None, help='Name of target file containing reduced embeddings')

    args = parser.parse_args()
    return args


if __name__ == '__main__':

    args = get_args()
    source_column = args.source_column
    data_path = args.data
    training_size = args.training_size

    if args.out_file_data is None:
        out_file_data = data_path.replace('.pkl', '_2d.pkl')
    else:
        out_file_data = args.out_file_data
    print('Target file name for data:', out_file_data)

    if args.out_file_reducer is None:
        out_file_reducer = "./2d_embedder"
    else:
        out_file_reducer = args.out_file_reducer
    print('Target file name for reducer:', out_file_reducer)

    print("0. Loading data...")
    df = pd.read_pickle(data_path)
    embeddings_all = df[source_column].to_list()

    print("1. Sampling training examples...")
    if len(embeddings_all) > training_size:
        train_embeddings = random.sample(embeddings_all, training_size)
    else:
        train_embeddings = embeddings_all
    print("\t...", len(train_embeddings), "embeddings used for training")

    print("2. Training 2d reducer...")
    embedder = ParametricUMAP(n_components=2).fit(train_embeddings)

    print("3. Saving 2d reducer...")
    embedder.save(out_file_reducer)

    print("4. Running model on all data...")
    reduced_embeddings = embedder.transform(embeddings_all)

    print("5. Saving 2d embeddings...")
    df['embedding_2d'] = reduced_embeddings.tolist()
    df.to_pickle(out_file_data)

    print("Done!")