import os
import argparse
import pandas as pd
from sentence_transformers import SentenceTransformer
from torch.cuda import is_available
from tqdm import tqdm
from extract_text_data import DATA_DIR, DATA_FILE

def get_args():
    """ Defines hyper-parameters. """
    parser = argparse.ArgumentParser('Run NLI model on corpus')

    # Add data arguments
    parser.add_argument('--data', default=f'{DATA_DIR}/{DATA_FILE}.csv', help='Name of data file')
    parser.add_argument('--source-column', type=str, default='text', help='Name of column contain input text')
    parser.add_argument('--model-name', type=str, default='all-mpnet-base-v2', help='Model name')
    parser.add_argument('--out-file', default=f'{DATA_DIR}/{DATA_FILE}_w_embeddings.csv', help='Name of target file')

    args = parser.parse_args()
    return args


def df_apply_sbert(classifier, sub_df, source_column, target_column="sbert_embedding"):
    texts = sub_df[source_column].to_list()
    embeddings = list(classifier.encode(texts))
    sub_df[target_column] = embeddings
    return sub_df


def run(classifier, dataframe, out_file, source_column):
    number_lines = len(dataframe)
    chunksize = 12

    if os.path.isfile(out_file):
        try:
            already_done = pd.read_csv(out_file)
            start_line = len(already_done)
        except Exception as exp:
            print(f"ERROR: {exp}")
            start_line = 0

    else:
        start_line = 0

    for i in tqdm(range(start_line, number_lines, chunksize)):

        sub_df = dataframe.iloc[i: i + chunksize]
        sub_df = df_apply_sbert(classifier, sub_df, source_column)

        if i == 0:
            sub_df.to_csv(out_file, mode='a', index=False)
        else:
            sub_df.to_csv(out_file, mode='a', index=False, header=False)


if __name__ == '__main__':

    args = get_args()
    source_column = args.source_column
    model_name = args.model_name
    data_path = args.data

    if args.out_file is None:
        target_path = data_path.replace('.csv', '_w_embeddings.csv')
    else:
        target_path = args.out_file
    print('Target file name:', target_path)

    print("0. Loading model...")
    use_cuda = is_available()
    if use_cuda:
        print('Using GPU')
        classifier = SentenceTransformer(model_name, device='cuda')
    else:
        print("Using CPU")
        classifier = SentenceTransformer(model_name)

    print("1. Loading data...")
    df = pd.read_csv(data_path)

    print("2. Running model...")
    run(classifier, df, target_path, source_column)

    print("Done!")

