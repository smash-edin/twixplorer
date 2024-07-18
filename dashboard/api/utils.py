import time
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from solr_class import print_this
from configs import ApplicationConfig_DATABASE
import re
def initialize_database():
    print_this("Initializing the system database")
    username = ""
    password = ""
    while username == "":
        username = input(f"Please enter the admin username: [{ApplicationConfig_DATABASE.USERNAME_MIN_LENGTH}-{ApplicationConfig_DATABASE.USERNAME_MAX_LENGTH} letters and numbers (no special chars and no spaces.)]: ")
        pattern = r"^(?!.*(.)\1{3,})[A-Za-z][A-Za-z0-9_-]{" + str(ApplicationConfig_DATABASE.USERNAME_MIN_LENGTH-1) + "," + str(ApplicationConfig_DATABASE.USERNAME_MAX_LENGTH-1) + "}$"
        if not re.match(pattern , username):
            print(f"ERROR: \nPlease re-enter the admin username with the following conditions:\n\tEnglish letters, Numbers, and the special chars ('-' or '_'),\n\tIt must start with a letter,\n\tIt must be {ApplicationConfig_DATABASE.USERNAME_MIN_LENGTH} to {ApplicationConfig_DATABASE.USERNAME_MAX_LENGTH} chars.")
            username = ""

    while password == "":
        import getpass
        password = getpass.getpass(prompt = f"Please enter the admin password [{ApplicationConfig_DATABASE.PASSWORD_MIN_LENGTH}-{ApplicationConfig_DATABASE.PASSWORD_MAX_LENGTH} chars, with special characters and no spaces.]: ")
        pattern = r"^(?!.*(.)\1{3,})[A-Za-z0-9_-]{" + str(ApplicationConfig_DATABASE.PASSWORD_MIN_LENGTH) + "," + str(ApplicationConfig_DATABASE.PASSWORD_MAX_LENGTH) + "}$"
        if not re.match(pattern , password):
            print("ERROR: \nPlease re-enter the admin password with the following conditions:\n\tEnglish letters, Numbers, and the special chars ('-' or '_'),\n\tIt must be 6 to 12 chars.")
            password = ""
    return username, password

""" This file contains util functions used by different back-end files """

def get_tf_idf(df, text_column, label_column, labels_list=None, n=40):
    """Function that return the N most frequent words for each topic.

    Args:
        :df: (pandas.DataFrame) Dataframe containing texts and their labels
        :text_column: (str) name of column containing the text from which to generate TF-IDF (i.e. "processed_text" or \
            "description")
        :label_column: (str) name of column containing the label of each text from which to generate TF-IDF (i.e. \
            "Topic" or "Community")
        :n: (int) Number of top words to return per topic.

    Returns:
        :dict: Dictionary with, as an entry for each topic, a list of dictionaries with the keys "text" (the word) and \
            "value" (the TF-IDF value for this word).
    """
    if len(df) == 0:
        return None
    start = time.time()

    df = df[df[text_column].apply(lambda x: isinstance(x, str) and len(x) > 0)]

    if not labels_list is None:
        df = df[df[label_column].isin(labels_list)]

    # Give unique IDs to texts
    m=len(df)
    df['Doc_ID'] = range(m)

    # Aggregate texts per group
    docs_per_group = df.groupby([label_column], as_index = False).agg({text_column: ' '.join})
    documents = docs_per_group[text_column].values

    if (len(documents)>0):
        # Get the frequency of each word per group
        count = CountVectorizer(ngram_range=(1, 1), stop_words="english").fit(documents)
        t = count.transform(documents).toarray()

        print("--> COUNTS:", t)

        w = t.sum(axis=1)
        tf = np.divide(t.T, w)
        sum_t = t.sum(axis=0)
        idf = np.log(np.divide(m, sum_t)).reshape(-1, 1)
        tf_idf = np.multiply(tf, idf)

        # Extract top N words per group
        words = count.get_feature_names_out()
        labels = list(docs_per_group[label_column])
        tf_idf_transposed = tf_idf.T
        indices = tf_idf_transposed.argsort()[:, -n:]
        top_n_words = {str(int(label)): [{"text": words[j], "value": tf_idf_transposed[i][j]} for j in indices[i]][::-1] for i, label in enumerate(labels)}

        # Print total time for this function to execute
        end = time.time()
        print("\t\t...time = %.1f" % (end - start))
        return top_n_words
    return {}


def get_request_components(req):
    """ Function to parse the input filters from the search query received from the front-end

    Args:
        :req: (dict) The dictionary containing the values in the query

    Returns:
        :tuple: the values for the source dataset, keywords list, the operator to apply to the keywords ("AND" or "OR"), \
        the filters (i.e. sentiment, language and country) and the limit on the number of results to retrieve from Solr
    """
    source = req['source'] if 'source' in req.keys() else None
    keywords_list = req['keywords'] if ('keywords' in req.keys()) else []
    keywords_list = [x.strip() for x in keywords_list.strip().split(',')] if type(keywords_list) == str else keywords_list
    keywords_list = list(set(keywords_list))
    filters = dict()
    filters["date_start"] = req['date_start'] if 'date_start' in req.keys() else None
    filters["date_end"] = req['date_end'] if 'date_end' in req.keys() else None
    filters["language"] = req['language'] if 'language' in req.keys() else None
    filters["sentiment"] = req['sentiment'] if 'sentiment' in req.keys() else None
    filters["location"] = req['location'] if 'location' in req.keys() else None
    filters["randomSeed"] = req['random_seed'] if 'random_seed' in req.keys() else 555
    filters["location_type"] = req['location_type'] if 'location_type' in req.keys() else None
    operator = req['operator'] if 'operator' in req.keys() else 'AND'
    limit = req['limit'] if 'limit' in req.keys() else MAX_VOL
    return source, keywords_list, filters, operator, limit