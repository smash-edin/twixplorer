import os

import umap
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer

from sentence_transformers import SentenceTransformer
from umap.parametric_umap import load_ParametricUMAP

from matplotlib.pyplot import get_cmap
from matplotlib.colors import rgb2hex

from bokeh.plotting import figure, show
from bokeh.models import HoverTool, ColumnDataSource, CategoricalColorMapper, ColorBar, CustomJSHover, OpenURL, TapTool
from bokeh.embed import json_item

from solr_class import *
from utils import get_request_components

CURRENT_PATH = os.path.dirname(__file__)
MAX_VOL = 100000

print_this("Loading models...")

CLASSIFIER = SentenceTransformer('all-mpnet-base-v2')
EMBEDDER_5D = load_ParametricUMAP('../../preprocessing/sentence-embeddings/5d_embedder')
EMBEDDER_2D = load_ParametricUMAP('../../preprocessing/sentence-embeddings/2d_embedder')

print_this("Models loaded successfully!")

"""This utils file contains all the function used by the topic_modelling API endpoint. """

def get_color(topic, cmap, max_label):
    """Function that returns the HEX color code for a topic given that topic's number, a colormap and the total
       number of topics.

    Args:
        :topic: (int) Topic number.
        :cmap: (matplotlib.colors.LinearSegmentedColormap) Matplotlib colormap.
        :max_label: (int) Total number of labels.

    Returns:
        :str: HEX color code
    """
    if topic == -1:
        return '#BDBDBD'
    return rgb2hex(cmap(topic/max_label))

def get_plot(df, bokeh_cmap=None):
    """Function that generates the Bokeh scatter plot used for the Topic Discovery component from the data contained in
    a dataframe and a given colormap.

    Args:
        :df: (pandas.DataFrame) Dataframe containing at least the columns "display_text" (tweet text to show on hover), \
            "x" and "y" (coordinates of tweet in scatter plot), "color" and "size" (visual features).
        :bokeh_cmap: (bokeh.models.CategoricalColorMapper, optional) Bokeh colormap object used to color datapoints in \
            the scatter plot based on their topic. If this argument is different from None, the \
            dataframe in df needs to have the column "Topic". Defaults to None.

    Returns:
        :bokeh.plotting.figure: Bokeh figure containing scatter plot of Topic Discovery
    """

    datasource = ColumnDataSource(df)
    plot_figure = figure(
        width=600,
        height=600,
        tools=('pan, wheel_zoom, reset', 'tap')
    )

    custom_hov = CustomJSHover(code="""
         special_vars.indices = special_vars.indices.slice(0,4)
         if (special_vars.indices.indexOf(special_vars.index) >= 0)
         {
             return " "
         }
         else
         {
             return " hidden "
         }
     """)

    url = "https://twitter.com/twitter/status/@id"
    taptool = plot_figure.select(type=TapTool)
    taptool.callback = OpenURL(url=url)

    if bokeh_cmap is None:
        plot_figure.add_tools(HoverTool(tooltips="""
        <div @y{custom}>
            <div style="padding-top:5px; padding-bottom:5px">
                <span style='font-size: 14px; color: #224499'>Text:</span>
                <span style='font-size: 14px'>@display_text</span>
            </div>
        </div>
        """, formatters={'@y':custom_hov}))
    else:
        plot_figure.add_tools(HoverTool(tooltips="""
        <div @y{custom}>
            <div style="padding-top:5px">
                <span style='font-size: 14px; color: #224499'>Text:</span>
                <span style='font-size: 14px'>@display_text</span>
            </div>
            <div style="padding-bottom:5px">
                <span style='font-size: 14px; color: #224499'>Topic:</span>
                <span style='font-size: 14px'>@Topic</span>
            </div>
        </div>
        """, formatters={'@y':custom_hov}))

        cb = ColorBar(color_mapper = bokeh_cmap, location = (5,6), title = "Topic Number")
        plot_figure.add_layout(cb, 'right')

    plot_figure.circle(
        'x',
        'y',
        source=datasource,
        color="color",
        line_alpha=0.6,
        fill_alpha=0.6,
        size='size'
    )
    plot_figure.grid.visible = False
    plot_figure.axis.visible = False
    return plot_figure

def compute_positive_negative(top_words, keyword):
    """ Function to determine the most characteristic words from positive and negative tweets in the current search \
        respectively. The results are added to the input dictionary "top_words" under the keys "Positive_Negative" \
        (for the most positive terms) and "Negative_Positive" (for the most negative terms).

    Args:
        :top_words: (dict) Dictionary containing the most frequent words in each sentiment split of the data
        :keyword: (str) The keyword of interest from those used to generate the report
    """
    positive_topics = set(top_words[keyword]['Positive'].keys()) if 'Positive' in top_words[keyword] and top_words[keyword]['Positive'] != None else set()
    negative_topics = set(top_words[keyword]['Negative'].keys()) if 'Negative' in top_words[keyword] and top_words[keyword]['Negative'] != None else set()

    top_words[keyword]['Positive_Negative'] = dict()
    top_words[keyword]['Negative_Positive'] = dict()
    for topic in positive_topics.intersection(negative_topics):
        print_this(topic)
        df1 = pd.DataFrame.from_records(top_words[keyword]['Positive'][topic])
        df2 = pd.DataFrame.from_records(top_words[keyword]['Negative'][topic])
        merged_df = pd.merge(df1, df2, on='text', how='outer')
        merged_df.fillna('', inplace=True)

        merged_pos_df = merged_df[merged_df['value_y']==""].sort_values(by='value_x', ascending=False).head(150)[['text','value_x']]
        merged_neg_df = merged_df[merged_df['value_x']==""].sort_values(by='value_y', ascending=False).head(150)[['text','value_y']]
        top_words[keyword]['Positive_Negative'][topic] = [{key if key != 'value_x' else 'value': value for key, value in row.items()} for row in merged_pos_df.to_dict(orient='records')]
        top_words[keyword]['Negative_Positive'][topic] = [{key if key != 'value_y' else 'value': value for key, value in row.items()} for row in merged_neg_df.to_dict(orient='records')]

    for topic in positive_topics - negative_topics:
        merged_df = pd.DataFrame.from_records(top_words[keyword]['Positive'][topic])
        merged_df.fillna('', inplace=True)
        merged_pos_df = merged_df.sort_values(by='value', ascending=False).head(150)[['text','value']]
        top_words[keyword]['Positive_Negative'][topic] = [{key: value for key, value in row.items()} for row in merged_pos_df.to_dict(orient='records')]

    for topic in negative_topics - positive_topics:
        merged_df = pd.DataFrame.from_records(top_words[keyword]['Negative'][topic])
        merged_df.fillna('', inplace=True)
        merged_neg_df = merged_df.sort_values(by='value', ascending=False).head(150)[['text','value']]
        top_words[keyword]['Negative_Positive'][topic] = [{key: value for key, value in row.items()} for row in merged_neg_df.to_dict(orient='records')]

def process_text(text):
    """Function that removes URLs and Twitter handles from the text of a tweet.

    Args:
        :text: (str) Original tweet.

    Returns:
        :str: New tweet processed such that URLs and twitter handles are removed.
    """
    new = " ".join([t for t in text.split() if t[:4] != "http"])
    new = " ".join([t for t in new.split() if t[0] !="@"])
    new = re.sub("[a-f0-9]{16}", "", new)
    return new


def format_display_text(text, line_len=55):
    """Function that formats text from tweet so that it is split over several lines, each no longer than a given
    number of characters.

    Args:
        :text: (str) Original tweet.
        :line_len: (int, optional) The maximal length of the line in number of characters. Defaults to 55.

    Returns:
        :str: tweet split over several lines.
    """
    tokens = text.split()
    new_text = ""
    line_count = 0
    for t in tokens:
        if (line_count + len(t) + 1) > line_len:
            new_text += "<br>"
            line_count = 0
        new_text += t + " "
        line_count += len(t) + 1
    return new_text


def get_topic_data(req):
    """Function that retrieves from Solr the data that corresponds to the filters "source" (name of Solr core),
    "keywords", "date_start", "date_end" and "operator".

    Args:
        :req: (dict) Query dictionary which must contain the fields "source" (str), "keywords" (list[str]), \
            "date_start" (str), "date_end" (str) and "operator" (str, must be "OR" or "AND").

    Returns:
        :dict or tuple: If successful, returns a dictionary containing the relevant data for the topic \
            discovery module, faceted by sentiment. Otherwise, returns a tuple containing a dictionary with an error \
            message and an error code.
    """
    source, keywords_list, filters, operator, limit = get_request_components(req)

    if source==None:
        resp = {"Error": "No data source specified, or wrong one provided!"}
        return make_response(jsonify(resp)), 400

    responses = dict()
    dataSource = SolrClass(filters=filters)
    query = dataSource.solr_query_builder(keywords_list, operator, limit, "TOPIC Utils")

    #for keyword in keywords_list:
    for keyword in query.keys():

        query_term = query[keyword]
        response,hits = dataSource.optimised_json_query_handler_topics(solr_core=source, keyword=query_term, rows= limit)

        if keyword == "" or keyword == None or keyword == "All":
            responses["All"] = response
        else:
            responses[keyword] = response

    return responses

def preprocess_data(df):
    """Function that creates the new columns "processed_text", "display_text", "x" and "y" in the dataframe containing
    the data used to generate the Topic Discovery scatterplot, and filters out duplicate tweets based on the field
    "process_text" (i.e. removes all duplicates when ignoring URLs and twitter handles).

    Args:
        :df: (pandas.DataFrame) Dataframe containing the tweets which will be used to generate the Topic Discovery \
            plot. It must contain the columns "full_text" (str, the tweet text) and "embedding_2d" (list, the two \
            dimensional embedding of the tweet).

    Returns:
        :pandas.DataFrame: The pre-processed dataframe containing the new fields "processed_text", "display_text", \
            "x" and "y".
    """
    print("Check 1:", len(df))
    try:
        # Remove duplicate tweets (ignoring URLs and Twitter handles)
        df["processed_text"] = df["full_text"].apply(process_text)
        df["display_text"] = df["full_text"].apply(format_display_text)
        df = df.drop_duplicates(subset=["processed_text"])
        print("Check 2:", len(df))
        # Sample 100K tweets if the total volume is greater than that
        if len(df) > MAX_VOL:
            df = df.sample(n=MAX_VOL)
        print("Check 3:", len(df))
        # Create a separate "x" and "y" coordinate field from the 2 dimensional tweet embedding
        df['x'] = df["embedding_2d"].apply(lambda x: x[0])
        df['y'] = df["embedding_2d"].apply(lambda x: x[1])
        return df
    except Exception as exp:
        return pd.DataFrame()
    
    
def get_network_plot(df, bokeh_cmap=None):
    datasource = ColumnDataSource(df)
    plot_figure = figure(
        width=600,
        height=600,
        tools=('pan, wheel_zoom, reset')
    )
    if bokeh_cmap is None:
        plot_figure.add_tools(HoverTool(tooltips="""
        <div>
            <div>
                <span style='font-size: 12px; color: #224499'>Node:</span>
                <span style='font-size: 12px'>@node, @desc, @community</span>
            </div>
        </div>
        """))
    else:
        plot_figure.add_tools(HoverTool(tooltips="""
        <div>
            <div>
                <span style='font-size: 12px; color: #224499'>Node:</span>
                <span style='font-size: 12px'>@node, @desc, @community</span>
            </div>
            
        </div>
        """))

        cb = ColorBar(color_mapper = bokeh_cmap, location = (5,6))
        plot_figure.add_layout(cb, 'right')
    
    plot_figure.circle(
        'x',
        'y',
        color="color",
        source=datasource,
        line_alpha=0.6,
        fill_alpha=0.6,
    )
    plot_figure.grid.visible = False
    plot_figure.axis.visible = False
    return plot_figure

