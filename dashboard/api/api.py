from configs import ApplicationConfig
from flask import Flask, request, jsonify, session, make_response
from flask_bcrypt import Bcrypt
from flask_cors import CORS, cross_origin
from model.models import db, User, Search
from datetime import datetime, timedelta
import time
import json
import jwt
import os
import copy
import pandas as pd
from solr_class import *
from topic_modelling_utils import *
from sna_utils import *
from utils import get_tf_idf, get_request_components, initialize_database
import sys
import traceback

with open(f'{os.path.abspath("../config")}/allowedOrigins.js') as dataFile:
    data = dataFile.read()
    obj = data[data.find('[') : data.rfind(']')+1]
    allowedOrigins = eval(obj)
    
"""This is the main Flask API file containing all API endpoints. This API is used to retrieve data from the Solr core,
in which the data is indexed, and process it into a format expected by the React UI.
"""

CURRENT_PATH = os.path.dirname(__file__)

app = Flask(__name__, template_folder='html')
app.config.from_object(ApplicationConfig)
CORS(app, supports_credentials=True, origins=allowedOrigins,  resources={r"/*": {"origins": allowedOrigins}})
bcrypt = Bcrypt(app)


db.init_app(app)
with app.app_context():
    db.create_all()

    if len(User.query.all()) == 0:
        username, password = initialize_database()
        hashed_password = bcrypt.generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, type="admin")
        db.session.add(new_user)
        db.session.commit()


top_n = 250

cached_tweets_folder = '../cached_tweets/'

if os.path.exists(cached_tweets_folder) == False:
    os.mkdir(cached_tweets_folder)

print_this(f"System is ready!")
# ================== AUTHENTICATION FUNCTIONS ==================

def refresh_session(user, data=None):
    """Function to refresh access to the user session if logged in and active (i.e. delay expiration of session).

    Returns:
        :dict: Contains an "accessToken" and a "username" field.
    """
    print_this('Refresh session called!')
    try:
        expiration = datetime.timestamp(datetime.now()+timedelta(weeks=app.config['ACCESS_TOKEN_TIMER']))
        accessToken = jwt.encode({
                'username': user.username,
                'exp': expiration
            },
            app.config['ACCESS_TOKEN_SECRET'])
        print_this(f"accessToken at refreshSession: {accessToken}!")
    except Exception as exp:
        print_this(f"Error: {exp}")
        return None

    expiration = datetime.timestamp(datetime.now()+timedelta(weeks=app.config['REFRESH_TOKEN_TIMER']))
    refreshToken = jwt.encode({
            'username': user.username,
            'exp': expiration
        },
        app.config['REFRESH_TOKEN_SECRET'])

    jsonResponse = {"accessToken": accessToken, "username":user.username, "userType": user.type}

    print_this(jsonResponse)

    if data != None:
        if type(data) == list:
            jsonResponse['data'] = data
        elif type(data) == dict:
            for k in data:
                jsonResponse[k] = data[k]

    resp = make_response(jsonify(jsonResponse))
    try:
        user.refreshToken = refreshToken
        db.session.commit()
        resp.set_cookie('jwt', user.refreshToken, app.config['REFRESH_TOKEN_TIMER']*60*60, httponly = True,  secure=False, samesite="None")
    except Exception as exp:
        print_this(f"Error: {exp}")
    return resp, refreshToken


def authenticated(refreshToken=None, check_admin=False):
    """ Function to authenticate using the refresh token.

    Args:
        :refreshToken: (str) Refresh token.
        :check_admin: (bool) Variable to specify if the user is admin.

    Returns:
        :bool: whether the user has been successfully authenticated """
    print_this(f'Authenticated called!\n{refreshToken}')
    temp_user = None
    if refreshToken != "" and refreshToken != None:
        if check_admin:
            temp_user = User.query.filter_by(refreshToken=refreshToken, type="admin").first()
        else:
            temp_user = User.query.filter_by(refreshToken=refreshToken).first()
    return temp_user != None

@app.route("/register_user", methods=["POST"])
def register_user():
    """API endpoint to register a new user.

    Query fields
        :user: (str) User's username.
        :pwd: (str) User's password.

    Response
        :dict or tuple: If registration is successful, returns a dictionary with an "id" (the new user's ID) and a "username" \
            field. Otherwise, return a dictionary containing the "error" field (error message) and an error code.
    """
    print_this(f"Register user")
    refreshToken = request.cookies.get('jwt')
    if authenticated(refreshToken, True):
        username = request.json['uname']
        password = request.json['pwd']

        hashed_password = bcrypt.generate_password_hash(password)

        user_exists = User.query.filter_by(username=username).first() is not None

        if user_exists:
            return jsonify({"error": "User already exists"}), 409

        new_user = User(username=username, password=hashed_password, type="user")
        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "id": new_user.id,
            "username": new_user.username
        })
    return json.dumps({"error": "Unauthorized!"}, ensure_ascii=False), 401


@app.route("/delete_user", methods=["POST"])
def delete_user():
    """API endpoint to delete a user.

    Query fields
        :user: (str) User's username.
        :pwd: (str) User's password.

    Response
        :dict or tuple: If registration is successful, returns a dictionary with an "id" (the new user's ID) and a "username" \
            field. Otherwise, return a dictionary containing the "error" field (error message) and an error code.
    """

    print_this(f"Deleting users called")
    refreshToken = request.cookies.get('jwt')
    if authenticated(refreshToken, True):
    
        user_ids = request.json['users']
        for user_id in user_ids:
            print_this(f"Deleting users {user_id}")
            user_exists = User.query.filter_by(id=user_id).first() is not None
            db.session.delete(User.query.filter_by(id=user_id).first())
            db.session.commit()

        users = [{"id": user_item.id, "username": user_item.username, "type": user_item.username} for user_item in User.query.all()]
        response = {"users": users}

        if user_exists:
            return json.dumps(response, ensure_ascii=False), 200
    return json.dumps({"error": "Unauthorized!"}, ensure_ascii=False), 401

@app.route("/get_users", methods=["POST"])
@cross_origin(origin='*',supports_credentials=True,headers=['Content-Type','Authorization'])
def get_users():
    """API endpoint to get the users.

    Response
        :dict or tuple: If registration is successful, returns a dictionary with an "id" (the new user's ID) and a "username" \
            field. Otherwise, return a dictionary containing the "error" field (error message) and an error code.
    """
    
    print_this(f"Getting users")
    refreshToken = request.cookies.get('jwt')
    if authenticated(refreshToken, True):
        if User.query.all() is not None:
            response = {"users": [{"id": user_item.id, "username": user_item.username, "type": user_item.type} for user_item in User.query.all() if user_item.type != "admin"]}
            return json.dumps(response, ensure_ascii=False), 200
        return json.dumps({"users": [{}]}, ensure_ascii=False), 200
    return json.dumps({"error": "Unauthorized!"}, ensure_ascii=False), 401




@app.route("/delete_report", methods=["POST"])
def delete_report():
    """API endpoint to delete a user.

    Query fields
        :user: (str) User's username.
        :pwd: (str) User's password.

    Response
        :dict or tuple: If registration is successful, returns a dictionary with an "id" (the new user's ID) and a "username" \
            field. Otherwise, return a dictionary containing the "error" field (error message) and an error code.
    """

    refreshToken = request.cookies.get('jwt')
    if authenticated(refreshToken, False):
        report_ids = request.json['reports']
        for report_id in report_ids:
            print_this(f"Deleting report: {report_id}")
            report_exists = Search.query.filter_by(id=report_id).first() is not None
            db.session.delete(Search.query.filter_by(id=report_id).first())
            db.session.commit()


        reports = [{"id": report.id, "reportName": report.reportName, "username": report.username, "creationTime": report.creationTime} for report in Search.query.all()]
        response = {"reports": reports}

        if report_exists:
            return json.dumps(response, ensure_ascii=False), 200
    return json.dumps({"error": "Unauthorized!"}, ensure_ascii=False), 401

@app.route("/save_report", methods=["POST"])
def save_report():
    """API endpoint to save a report.

    Query fields
        :data: (str)

    Response
        a message to show the outcomes.
    """
    print_this("saveReport called!")

    refreshToken = request.cookies.get('jwt')
    if authenticated(refreshToken, False):
        data= request.json.get('data','')
        token= data.get('token','')
        reportName= data.get('name','')
        tempReportName = reportName

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        temp_user = User.query.filter_by(refreshToken=refreshToken).first()

        try:
            sessionInfoCookie = jwt.decode(jwt=refreshToken, key=app.config['REFRESH_TOKEN_SECRET'], algorithms=['HS256'])
        except Exception as exp:
            resp = make_response(jsonify({"error": "Unauthorized!"}))
            return resp, 401
        if temp_user:
            if temp_user.username == sessionInfoCookie['username']:

                previous_search = Search.query.filter_by(username=temp_user.username, reportName= tempReportName)
                i = 1
                while len(previous_search.all()) > 0:
                    tempReportName = f"{reportName}({i})"
                    previous_search = Search.query.filter_by(username=temp_user.username, reportName= tempReportName)
                    print_this(f"search item found, data will be updated from {reportName} to {tempReportName}")
                    i += 1

                new_search = Search(username=temp_user.username, token=token, reportName=tempReportName, creationTime= timestamp)
                db.session.add(new_search)
                db.session.commit()

                resp = make_response(jsonify({"Message": f"Report saved with name {tempReportName}."}))
                print(f"This is the user name: {temp_user.username}")
                return resp, 200
    return json.dumps({"error": "Unauthorized!"}, ensure_ascii=False), 401

@app.route('/logout', methods=["POST"])
@cross_origin(origin='*',supports_credentials=True,headers=['Content-Type','Authorization'])
def logout():
    """API endpoint to log out user from their personal session.

    Query fields:
        :accessToken: (str) User's access token.

    Response:
        :tuple: Contains a dictionary with a status message (under "Message" field) and an error code.
    """
    try:
        if request.is_json:
            accessToken = request.json.get('accessToken')
            if "accessToken" in session.keys():
                if accessToken == session["accessToken"]:
                    session.pop('accessToken')

        refreshToken = request.cookies.get('jwt')
        temp_user = User.query.filter_by(refreshToken=refreshToken).first()
        if temp_user != None:
            if temp_user.refreshToken:
                temp_user.refreshToken = ""

                db.session.commit()
        resp = make_response(jsonify({"Message": "Logged out!"}))
        resp.delete_cookie('jwt')

        return resp, 200
    except Exception as exp:
        resp = make_response(jsonify({"Message": "Logged out!"}))
        resp.delete_cookie('jwt')
        return resp, 200

@app.route('/auth')
@cross_origin(origin='*',supports_credentials=True,headers=['Content-Type','Authorization'])
def auth():
    """API endpoint that launches the authentication process. If an existing user session is active, the login is \
    performed automatically. Otherwise, front-end is notified that the user needs to log in.

    Response:
        :tuple: Contains a dictionary with the bearer's access token (if login is successful) or appropriate \
            error message otherwise, and an error code.
    """
    users_exists = User.query.all()
    bearer = None
    if request.headers.get('Authorization'):
        if len(request.headers.get('Authorization')) > 1:
            bearer = request.headers.get('Authorization')
    elif request.headers.get('authorization'):
        if len(request.headers.get('authorization')) > 1:
            bearer = request.headers.get('authorization')
    msg = ""
    sessionInfo = None
    if bearer != None:
        try:
            bearer = bearer.split(' ')[1]
            sessionInfo = jwt.decode(jwt=bearer, key=app.config['ACCESS_TOKEN_SECRET'], algorithms=['HS256'])
        except Exception as exp:
            sessionInfo = None
            print("Error" + exp)
    if sessionInfo != None:
        return jsonify({"accessToken": bearer}), 200
    else:
        refreshToken = request.cookies.get('jwt')
        if refreshToken:
            temp_user = User.query.filter_by(refreshToken=refreshToken).first()
            try:
                sessionInfoCookie = jwt.decode(jwt=refreshToken, key=app.config['REFRESH_TOKEN_SECRET'], algorithms=['HS256'])
            except Exception as exp:
                print_this(f"Exception occurred at auth GET: { exp }")
                if temp_user != None:
                    if temp_user.refreshToken!="":
                        temp_user.refreshToken = ""
                        db.session.commit()
                    resp = make_response(jsonify({"Message": "Not logged in!"}))
                    resp.delete_cookie('jwt')
                    if bearer:
                        resp.pop('accessToken')
                    return resp, 401
            if temp_user:
                if temp_user.username == sessionInfoCookie['username']:
                    print_this("AT AUTH GET COMMIT!")
                    resp, newRefreshToken = refresh_session(temp_user)
                    return resp, 200
    return authentication()


@app.route('/auth', methods=["POST"])
@cross_origin(origin='*',supports_credentials=True,headers=['Content-Type','Authorization'])
def authentication():
    """API endpoint that enables the user to log into their personal session (e.g. to save and load reports).

    Query fields:
        :user: (str) User's username.
        :pwd: (str) User's password.

    Response:
        :tuple: Contains a dictionary with a status message (under “error” field) and an error code.
    """
    print_this("TRYING TO AUTHENTICATE!")
    print_this(f"request: {request}!")
    try:
        if request.is_json:
            username = request.json["user"]
            pwd = request.json["pwd"]
            if username:
                hashed_password = bcrypt.generate_password_hash(pwd)
                temp_user = User.query.filter_by(username=username).first()

                if temp_user is None:
                    return jsonify({"error": "Unauthorized\nWrong username or password"}), 401

                if type(username) == str:
                    if not bcrypt.check_password_hash(temp_user.password, pwd):
                        return jsonify({"error":"Unauthorized\nWrong username or password"}), 401

                    print_this(f"AT AUTH POST!")
                    resp, newRefreshToken = refresh_session(temp_user)
                    print_this(f"AT AUTH POST - after refresh!")
                    return resp, 200
            else:
                return jsonify({"error":"Unauthorized!"}), 401
        else:
            resp = make_response(jsonify({"accessToken": ""}))
            print_this('Unauthorized! logged out!')
            return resp, 200
        print_this('Nothing done!!')
        return jsonify({"error":"Unauthorized!"}), 401
    except Exception as exp:
        print_this(f"exception: {exp}")
        resp = make_response(jsonify({"error": "Unauthorized" + str(exp), "accessToken": ""}))
        return resp, 401


@app.route('/load_report', methods=["GET"])
@cross_origin(origin='*',supports_credentials=True,headers=['Content-Type','Authorization'])
def load_reports():
    """API endpoint that enables access to the "Analysis" page in the dashboard from cached credentials

    Response:
        :dict: Contains the single field "error" with the error message.
        :int: Error code.
    """
    print_this(f"Load reports called with GET methods...")
    refreshToken = request.cookies.get('jwt')

    resp = None
    if authenticated(refreshToken, False):
        print_this("After authenticated!")
        try:
            temp_user = User.query.filter_by(refreshToken=refreshToken).first()
            sessionInfoCookie = jwt.decode(jwt=refreshToken, key=app.config['REFRESH_TOKEN_SECRET'], algorithms=['HS256'])
            if temp_user != None:
                if temp_user.username == sessionInfoCookie['username']:
                    resp, newRefreshToken = refresh_session(temp_user)
                    return resp, 200
        except Exception as exp:
            resp = None
    resp = make_response(jsonify({"response:":"Unauthorized!"}))
    return resp, 401


@app.route('/load_report', methods=["POST"])
@cross_origin(origin='*',supports_credentials=True,headers=['Content-Type','Authorization'])
def update_reports():
    """API endpoint that enables access to the "Analysis" page in the dashboard from cached credentials

    Response:
        :dict: Contains the single field "error" with the error message.
        :int: Error code.
    """
    refreshToken = request.cookies.get('jwt')

    print_this(f"Load report with POST methods")
    resp = None
    if authenticated(refreshToken, False):
        try:
            temp_user = User.query.filter_by(refreshToken=refreshToken).first()
            sessionInfoCookie = jwt.decode(jwt=refreshToken, key=app.config['REFRESH_TOKEN_SECRET'], algorithms=['HS256'])

            if temp_user != None:
                if temp_user.username == sessionInfoCookie['username']:
                    if temp_user.type == "admin":
                        items = Search.query.all()
                    elif temp_user.type == "user":
                        items = Search.query.filter_by(username=temp_user.username)
                    else:
                        items = []
                    items_response = [{"id": item.id, "username": item.username, "reportName": item.reportName ,"token": item.token, "creationTime": item.creationTime} for item in items]
                    resp, newRefreshToken = refresh_session(temp_user, items_response)
                    return resp, 200
        except Exception as exp:
            print_this(f"Error {exp}")
            resp = None
    print_this("At load page, It went wrong! !")
    return json.dumps({"error": "Unauthorized!"}, ensure_ascii=False), 401

@app.route('/admin', methods=["GET"])
@cross_origin(origin='*',supports_credentials=True,headers=['Content-Type','Authorization'])
def admin():
    """API endpoint that enables access to the "Analysis" page in the dashboard from cached credentials

    Response:
        :dict: Contains the single field "error" with the error message.
        :int: Error code.
    """
    refreshToken = request.cookies.get('jwt')
    resp = None
    if authenticated(refreshToken, True):
        print_this('Admin API called!')
        try:
            temp_user = User.query.filter_by(refreshToken=refreshToken).first()
            sessionInfoCookie = jwt.decode(jwt=refreshToken, key=app.config['REFRESH_TOKEN_SECRET'], algorithms=['HS256'])
            
            if temp_user != None:
                if temp_user.username == sessionInfoCookie['username'] and temp_user.type == "admin":
                    resp, newRefreshToken = refresh_session(temp_user)
        except Exception as exp:
            resp = None
    if resp != None:
        return resp, 200
    return json.dumps({"error": "Unauthorized!"}, ensure_ascii=False), 401

# ================== MAIN REPORT FUNCTIONS ==================


languages_file_path = os.path.join(CURRENT_PATH, '.data/languages.csv')
countries_file_path = os.path.join(CURRENT_PATH, '.data/countries_codes_english.csv')

languages = list(pd.read_csv(languages_file_path, delimiter=";")['language'])
countries = list(pd.read_csv(countries_file_path)['name'])

@app.route("/get_countries_list", methods=["GET"])
@cross_origin(origin='*',supports_credentials=True,headers=['Content-Type','Authorization'])
def get_countries_list():
    """API endpoint that returns the list of valid countries (stored on file) for location graph.

    Response:
        :dict: Jsonified CSV file with list of countries with their codes.
    """
    try:
        resp = make_response(jsonify(countries))
        return resp, 200
    except Exception as exp:
        print_this(f"Error getting countries list! {exp}")
        return make_response(jsonify({"error": "Error getting countries list!"})), 401
    return make_response(jsonify({"error": "Unauthorized!"})), 401


@app.route("/get_languages_list", methods=["GET"])
@cross_origin(origin='*',supports_credentials=True,headers=['Content-Type','Authorization'])
def get_languages_list():
    """API endpoint that returns the list of valid languages (stored on file) for language graph.

    Response:
        :dict: Jsonified list of languages.
    """
    try:
        resp = make_response(jsonify(languages))
        return resp, 200
    except Exception as exp:
        print_this(f"Error getting languages list! {exp}")
        return make_response(jsonify({"error": "Error getting languages list!"})), 401
    return make_response(jsonify({"error": "Unauthorized!"})), 401


@app.route("/api/search", methods=["POST"])
@cross_origin(origin='*',supports_credentials=True,headers=['Content-Type','Authorization'])
def search():
    """API endpoint that returns the relevant data from Solr for the main report.

    Query fields:
        :source: (str) Dataset to query from in Solr.
        :date_start: (str) Start of the date range (format YYYY-MM-DD, by default "").
        :date_end: (str) End of the date range (format YYYY-MM-DD, by default "").
        :keywords: (str) Comma-separated list of keywords to match in text (e.g. "keyword1, keyword2", by default "").
        :operator: (str) Determines whether to retrieve data that matches all keywords ("AND") or at least one of the \
            keywords ("OR", by default "OR").
        :nb_topics: (int) Number of cluster to group data into in Topic Discovery module.
        :claim: (str) Claim to be projected into the data in Topic Discovery module.
        :random_seed: (int) Random seed to make random selection of data in Topic Discovery Module (i.e. when volume is \
            greater than 100K) deterministic.
        :language: (str) Language of data, by default "All".
        :sentiment: (str) Sentiment of data (choice between "All", "Positive", "Neutral", "Negative"). By default "All"
        :location: (str) Country of data, by default "All".
        :location_type: (str) Whether country corresponds to "author" or "tweet". By default "author"

    Response:
        :hits: (int) Total volume of tweets that matched the query.
        :show_report: (bool) Whether the query was successful (i.e. results were found), defines if report should be \
          shown in front-end.
        :dataSource: (str) Dataset queried from in Solr.
        :source_text: (str) Display name of dataset queried from in Solr.
        :operator: (str) Determines whether data retrieved matched all keywords at once ("AND") or at least one of the \
            keywords ("OR", by default "OR").
        :report: (dict) The report contains a different entry for each keyword from the query. This entry is itself a \
            dictionary with the following fields:

            * count: (int) Number of datapoints that match this keyword
            * mentions: (dict[list]) Number of mentions per user, faceted by sentiment (i.e. of the text)
            * retweeted: (dict[list]) Number of retweets by user, faceted by sentiment (i.e. of the text)
            * retweeters: (dict[list]) Number of retweets per user, faceted by sentiment (i.e. of the text)
            * Languages_Distributions: (list[dict]) Number of tweets per language. Each dictionary contains a "Count" \
              and "Language" field
            * tweets_languages_by_sentiments: (dict[list]) Number of tweets per day, faceted by sentiment and language
            * Sentiment_per_language: (dict[list]) Number of tweets per language, faceted by sentiment
            * Sentiments_Distributions: (dict[list]) Number of tweets per day, faceted by sentiment
            * emojis: (dict[list]) Count per emoji, faceted by sentiment
            * media: (dict[list]) Count per media URL, faceted by sentiment
            * top_tweets: (dict[list]) Top 10K most retweeted tweets in dataset per sentiment, with id, date of \
              publication, text, language, location and retweet count
            * top_users: (dict[list]) Top 10K most retweeted users in dataset per sentiment, with user ID, screenname, \
              description, language, location and retweet count
            * urls: (dict[list]) Count per URL, faceted by sentiment
            * user_screen_name: (dict[list]) Count per user screenname, faceted by sentiment
            * hashtags: (dict[list]) Count per hashtag, faceted by sentiment
            * processed_desc_tokens: (dict[list]) Count per word from user descriptions, faceted by sentiment
            * processed_tokens: (dict[list]) Count per word from text, faceted by sentiment
            * traffic: (list[dict]) Number of tweets per day. Each dictionary contains a "Count" and "Date" field
            * users_locations_by_languages: (dict[list]) Number of users per region, faceted by language
            * users_locations_by_sentiments: (dict[list]) Number of users per region, faceted by sentiment
            * tweets_locations_by_sentiments: (dict[list]) Number of tweets per region, faceted by sentiment
            * tweets_locations_by_languages: (dict[list]) Number of tweets per region, faceted by language
    """
    print_this("Search API called!")
    refreshToken = request.cookies.get('jwt')
    req = request.get_json()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    if authenticated(refreshToken, False):
        try:
            temp_user = User.query.filter_by(refreshToken=refreshToken).first()
            sessionInfoCookie = jwt.decode(jwt=refreshToken, key=app.config['REFRESH_TOKEN_SECRET'], algorithms=['HS256'])
            if temp_user != None:
                if temp_user.username == sessionInfoCookie['username']:
                    source, keywords_list, filters, operator, limit = get_request_components(req['data'])

                    source_text = req['data']['source_text'] if 'source_text' in req['data'].keys() else ''
                    count = int(req['data']['count']) if 'count' in req['data'].keys() else 250
                    num_of_rows = req['data']['num_of_rows'] if 'num_of_rows' in req['data'].keys() else 'use_all'

                    if source==None:
                        resp = make_response(jsonify({"Error": "No data source specified, or wrong data source provided!"}))
                        return resp, 400

                    dataSource = SolrClass(filters=filters)
                    start = datetime.now()
                    report,hits = dataSource.optimised_json_query_handler(solr_core=source, keywords=keywords_list, operator=operator, limit=limit, top_n=count)
                    end = datetime.now()
                    keywords = [x for x in report.keys() if x != "All"]
                    for k in list(report.keys()):
                        if report[k]['count'] == 0:
                            report.pop(k)
                    print_this(f"Time taken to get data from Solr: {end-start}")
                    print_this(f'Hits are : {hits}')
                    resp, newRefreshToken = refresh_session(temp_user, {'report':report,'hits':hits, 'keywords': keywords, 'show_report':True, 'dataSource':source, 'operator':operator, 'source_text':source_text})
                    return resp, 200
        except Exception as exp:
            print_this(f"Search {exp}")
            print_this(traceback.format_exc())
            resp = make_response(jsonify({"Message": "Not logged in!"}))
            return resp, 401
    return make_response(jsonify({"Message": "Unauthorized!"})), 401




@app.route("/api/social_network_analysis", methods=["POST"])
@cross_origin(origin='*',supports_credentials=True,headers=['Content-Type','Authorization'])
def social_network_analysis():
    """API endpoint to generate results for social network analysis.

    Query fields
        :user: (str) User's username.
        :pwd: (str) User's password.

        :keyword: (str) Keyword filter as string
        :keywords: (list[str]) Keywords as list
        :date_start: (str) Start date as YYYY-MM-DD (None if no start date is used)
        :date_end: (str) End date as YYYY-MM-DD (None if no end date is used)
        :limit: (int) Maximum number of results returned
        :source: (str) Dataset to source data  from
        :operator: (str) Whether keywords should appear in the same tweets ("AND") or not necessarily ("OR")
        :random_seed: (float) Random seed to make random parts of function deterministic
        :language: (str) Language to filter data by
        :sentiment: (str) Sentiment to filter data by
        :location: (str) Country to filter data by
        :location_type: (str) Whether the country used is that of the user or the tweet
        :nb_communities": (int) How many of the top communities to highlight on the visualisation

    Response
        :dict or tuple: If user is correctly authenticated, returns a dictionary with the field "sna_figure" (which \
        contains the Bokeh plots for the social network analysis), "network_stats" (the values to populate the \
        "Communities Stats" component in the front-end) and "communities_traffic" (the values to populate the \
        "Communities tweeting" component in the front-end)

    """
    print_this("SNA called!")
    refreshToken = request.cookies.get('jwt')

    if authenticated(refreshToken, False):
        req = request.get_json()
        req = req['data']
        max_label = req["nb_communities"]
        interaction = req['interaction'] if 'interaction' in req.keys() else 'retweet'
        responses = get_sna_data(req, interaction)

        if responses!= None and len(responses) > 0:

            keywords = list(responses.keys())
            mapping = {
                    'All sentiments': 'All Sentiments',
                    'Positive': 'Positive',
                    'Negative': 'Negative',
                    'Neutral': 'Neutral'}
            plots_list = dict()
            colors_list = dict()
            top_words_list = dict()
            network_stats_all = dict()
            communities_traffic = dict()
            for keyword in keywords:
                print_this(f"==> {keywords} ==>")
                resp = responses[keyword]

                df_sub = resp['network_df']
                nodes_all = resp['nodes_df']
                try:
                    nodes_all = nodes_all.drop_duplicates(subset=['node'])
                    print("NB NODES BEFORE FILTERING OUT 0:", len(nodes_all))
                    nodes_all = nodes_all[nodes_all["community"] != 0]
                    print("NB NODES AFTER FILTERING OUT 0:", len(nodes_all))
                    network_stats_all[keyword] = resp['network_stats']['sentiments']

                    labels_all = nodes_all['community'].value_counts().index.to_list()
                    print_this(f"nodes_all: {nodes_all}")
                    comm_to_rank = {l: idx for idx,l in enumerate(labels_all) if idx < max_label}

                    nb_labels = min(len(labels_all),max_label)
                    cmap = get_cmap('hsv_r')
                    labels = labels_all[0:nb_labels]

                    communities_traffic[keyword] = {str(k): resp['network_stats']['communities_traffic'][k] for k in labels if k in resp['network_stats']['communities_traffic']}
                    print_this(f"keyword : {keyword}")
                    category_color_mapping = {x: get_color(comm_to_rank[x], cmap, max_label) if x in comm_to_rank else get_color(-1, cmap, max_label) for x in labels_all}
                    nodes_all['color'] = nodes_all['community'].apply(lambda x: category_color_mapping[x])

                    colors_list[keyword] = {str(c): category_color_mapping[c] for c in category_color_mapping}

                    if df_sub is not None and len(df_sub) > 0:
                        if len(df_sub) > 0 and len(nodes_all) > 0:
                            if len(nodes_all) > 0:
                                nodes = nodes_all
                                print("\tAfter filter 1:", len(nodes))

                                nodes = nodes[nodes['x']!=""]
                                print("\tAfter filter 2:", len(nodes))
                                bokeh_cmap = CategoricalColorMapper(factors=[str(l) for l in labels], palette=[get_color(comm_to_rank[l], cmap, max_label) for l in labels])
                                bokeh_cmap_cop = copy.deepcopy(bokeh_cmap)
                                plot = json_item(get_network_plot(nodes, bokeh_cmap_cop))
                                top_words = get_tf_idf(nodes, "desc", "community", labels_list=labels)

                            else:
                                plot = None
                            plots_list[keyword] = plot
                            top_words_list[keyword] = top_words
                        else:
                            plots_list[keyword] = None
                            top_words_list[keyword] = []
                except Exception as exp:
                    print_this(f"ERROR :: {exp}")
                    plots_list[keyword] = None
                    top_words_list[keyword] = []

            return json.dumps({"sna_figure": plots_list, "network_stats": network_stats_all, "communities_traffic": communities_traffic, "communities_colors": colors_list, "top_words": top_words_list})
        return json.dumps({"sna_figure": "", "network_stats": [], "communities_traffic": []})
    return make_response(jsonify({"Message": "Unauthorized!"})), 401

@app.route("/api/topic_modelling", methods=["POST"])
@cross_origin(origin='*',supports_credentials=True,headers=['Content-Type','Authorization'])
def topic_modelling():
    """API endpoint that returns relevant information for the Topic Discovery scatter plots and topic wordclouds.

    Query fields:
        :source: (str) Dataset to query from in Solr.
        :date_start: (str) Start of the date range (format YYYY-MM-DD, by default "").
        :date_end: (str) End of the date range (format YYYY-MM-DD, by default "").
        :keywords: (list[str]) List of keywords to match in text.
        :operator: (str) Determines whether to retrieve data that matches all keywords ("AND") or at least one of the \
            keywords ("OR", by default "OR").
        :nb_topics: (int) Number of cluster to group data into.
        :claim: (str) Claim to be projected into the same multi-dimensional space as the data.
        :random_seed: (int) Random seed to make random selection of data (i.e. when volume is greater than 100K) \
            deterministic.
        :language: (str) Language to filter data by.
        :sentiment: (str) Sentiment to filter data by.

    Output:
        :figures: (dict[dict[bokeh.plotting.figure]]) Bokeh figures per keyword (outter dict) and sentiment \
            (inner dict).
        :top_words: (dict[dict[list]]) Words with the greatest TF-IDF per keyword (outter dict) and sentiment (inner \
            dict). Each element in the inner dict is a list of dictionaries, with a "text" (str, the word) and "value" \
            (float, TF-IDF value) field.
    """
    print_this("Topic Modelling endpoint called!")
    refreshToken = request.cookies.get('jwt')
    if authenticated(refreshToken, False):
        start = time.time()

        # Get API request header
        req = request.get_json()
        req = req['data']

        rel_sentiments = ['All sentiments', 'Positive', 'Negative', 'Neutral'] if req["sentiment"] == "All" else [req["sentiment"]]

        # Get relevant data from Solr for the current request
        responses = get_topic_data(req)
        keywords = list(responses.keys())

        # Generate empty object in which results will be stored
        plots_list = dict() # Info for Bokeh plots
        top_words = None if req["nb_topics"] == 0 else {k: dict() for k in keywords} # Info for topic wordclouds

        # Get the data that corresponds to the "All" keyword
        if len(keywords) > 1:
            df_ALL = pd.concat([pd.DataFrame(responses[k]) for k in keywords if k != "All"]).drop_duplicates(["full_text"])
            df_ALL = preprocess_data(df_ALL)
        else:
            df_ALL = pd.DataFrame(responses[keywords[0]])
            df_ALL = preprocess_data(df_ALL)

        # If the dataframe with the data does not contain the field "full_text", return an empty results dictionary.
        if not 'full_text' in df_ALL.columns:
            return json.dumps({"figures": "", "top_words": []})

        # Generate the "Topic" field in the dataframe for the data corresponding to the keyword "All"
        if req["nb_topics"] == 0:
            # If the number of topics specified is 0, all topics are None
            df_ALL['Topic'] = [None] * len(df_ALL)
        else:
            # Otherwise, tweets are labelled with topic numbers by applying the K-means algorithm to the tweets'
            # 5d embeddings
            umap_embeddings = df_ALL["embedding_5d"].to_list()
            model = KMeans(n_clusters=req["nb_topics"])
            model.fit(umap_embeddings)
            yhat = model.predict(umap_embeddings)
            df_ALL['Topic'] = yhat

        # Set the "Size" of all tweets in the scatter plot to be equal to 4
        df_ALL["size"] = [4] * len(df_ALL)

        # Generate the "color" field in the dataframe for the data corresponding to the keyword "All"
        if req["nb_topics"] == 0:
            # If the number of topics specified is 0, all the tweets in the scatter plot are colored in grey
            df_ALL["color"] = ['#BDBDBD'] * len(df_ALL)
            bokeh_cmap = None
        else:
            # Otherwise, the color is obtained from the topic number using the "get_color" function
            labels = sorted(list(set(df_ALL["Topic"].to_list())))
            max_label = max(labels) + 1
            cmap = get_cmap('hsv_r')
            bokeh_cmap = CategoricalColorMapper(factors=[str(l) for l in labels], palette=[get_color(l, cmap, max_label) for l in labels])
            df_ALL["color"] = df_ALL["Topic"].apply(lambda x: get_color(x, cmap, max_label))

        # The following code is concerned with adding a custom claim (from the "claim" argument from query header) onto the
        # Topic Discovery scatter plot

        new_row = None
        if req["claim"].strip() != "":

            # Use the SBERT classifier, the parametric UMAP embedder to reduce 768 dimensional embeddings to 5 dimensions
            # and that to reduce 5 dimensional embeddings to 2 dimensions
            global CLASSIFIER
            global EMBEDDER_5D
            global EMBEDDER_2D

            # Obtain different encodings for the "claim" query argument
            encoding = CLASSIFIER.encode(req["claim"])
            encoding_5d = EMBEDDER_5D.transform([encoding])[0]
            encoding_2d = EMBEDDER_2D.transform([encoding_5d])[0]

            # Create new row to append to dataframe
            new_row = {"display_text": req["claim"], "color": "#000000", "x": encoding_2d[0], "y": encoding_2d[1], "size": 12}

        for keyword in keywords:

            plots_list[keyword] = dict()

            # Get the data that corresponds to the current keyword
            if keyword == "All" or len(keywords) == 1:
                df_sub = df_ALL
            else:
                df = pd.DataFrame(responses[keyword])
                df_sub = preprocess_data(df)
                # Merge the Topic, color and size fields obtained above from df_ALL with the data for the current keyword
                # This has been added to solve the empty df_sub DataFrame.
                if len(df_sub) > 0:
                    df_sub = pd.merge(df_sub, df_ALL[["id", "Topic", "color", "size"]], on="id", how="inner")
                else:
                    df_sub = df_ALL[["id", "sentiment","Topic", "color", "size"]].sample(0)

            mapping = {
                'All sentiments': 'All Sentiments',
                'Positive': 'Positive',
                'Negative': 'Negative',
                'Neutral': 'Neutral'}

            # Generate the Topic Discovery scatter plot for each sentiment
            for sentiment in rel_sentiments:

                if sentiment == 'All sentiments':
                    df_rel = df_sub
                else:
                    df_rel = df_sub[df_sub["sentiment"] == sentiment]

                print("Nb tweets:", keyword, sentiment, len(df_rel))

                # Add the datapoint for the "claim" query argument onto the scatter plot
                if not new_row is None:
                    df_rel = pd.concat([df_rel, pd.DataFrame([new_row])])

                # If tweets are labelled with topics, generate the TF-IDF info for each topic (for topic wordclouds)
                if req["nb_topics"] > 0:
                    top_words[keyword][mapping[sentiment]] = get_tf_idf(df_rel, "processed_text", "Topic")

                # Append scatter plot to empty results object
                if len(df_rel) == 0:
                    plot = None
                else:
                    bokeh_cmap_cop = copy.deepcopy(bokeh_cmap)
                    plot = json_item(get_plot(df_rel, bokeh_cmap=bokeh_cmap_cop))

                plots_list[keyword][mapping[sentiment]] = plot

            if top_words != None:
                compute_positive_negative(top_words, keyword)

        end = time.time()
        print("\t\t...time = %.1f" % (end - start))

        return json.dumps({"figures": plots_list, "top_words": top_words})
    return make_response(jsonify({"Message": "Unauthorized!"})), 401


if __name__ == "main":
    app.run(debug=True)