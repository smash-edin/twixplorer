import os
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource, ColorBar, CustomJSHover, OpenURL, TapTool

from solr_class import *
from utils import get_request_components

CURRENT_PATH = os.path.dirname(__file__)

"""This utils file contains all the function used by the SNA API endpoint. """
    
def get_network_plot(df, bokeh_cmap):
    """ A function to generate the Bokeh visualisation for the social network analysis.

    Args:
        df (pandas.DataFrame): dataframe containing user data (username, descriptio, community, x and y coordinates)
        interaction (bokeh.models.CategoricalColorMapper): color map for communities

    Returns:
        bpkeh.plotting.figure: A Bokeh visualisation of users in the retweet space
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

    url = "https://twitter.com/@node"
    taptool = plot_figure.select(type=TapTool)
    taptool.callback = OpenURL(url=url)

    plot_figure.add_tools(HoverTool(tooltips="""
    <div @y{custom}>
        <div style="padding-top:5px">
            <span style='font-size: 14px; color: #224499'>Username:</span>
            <span style='font-size: 14px'>@node</span>
        </div>
        <div>
            <span style='font-size: 14px; color: #224499'>Description:</span>
            <span style='font-size: 14px'>@desc</span>
        </div>
        <div style="padding-bottom:5px">
            <span style='font-size: 14px; color: #224499'>Community:</span>
            <span style='font-size: 14px'>@community</span>
        </div>
    </div>
    """, formatters={'@y':custom_hov}))

    cb = ColorBar(color_mapper = bokeh_cmap, location = (5,6), title = "Community Number")
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


def get_sna_data(req, interaction):
    """A function to get the data for the SNA by calling the corresponding function at SolrClass.

    Args:
        req (dict): request filters/parameters.
        interaction (str): network type (retweet, reply)

    Returns:
        dict: A dict of dataframes for the network and nodes, and a dataframe for the network stats.
    """
    source, keywords_list, filters, operator, limit = get_request_components(req)

    if source==None:
        resp = {"Error": "No data source specified, or wrong one provided!"}
        return make_response(jsonify(resp)), 400

    dataSource = SolrClass(filters=filters)
    responses = dict()

    query = dataSource.solr_query_builder(keywords_list, operator, limit, "SNA Utils")

    for keyword in query.keys():
        query_term = query[keyword]
        print_this(query_term)

        network_df, nodes_df = dataSource.get_network_of_users(solr_core=source, keyword=query_term, interaction=interaction)
        network_stats = dataSource.get_network_stats(solr_core=source, keyword=query_term, interaction=interaction, limit=limit)

        if keyword == None or keyword == "" or keyword == "All":
            responses["All"] = {'network_df': network_df, 'nodes_df': nodes_df, 'network_stats': network_stats}
        else:
            responses[keyword] = {'network_df': network_df, 'nodes_df': nodes_df, 'network_stats': network_stats}
    return responses
    