# TwiXplorer Discovery Dashboard

This folder contains the code for the React front-end (under src sub-folder) and Flask back-end (under api sub-folder) for the TwiXplorer dashboard.  

The **docs** sub-folder inside **api** contains the HTML documentation for this API. You can download the docs folder and then open the file _build/html/index.html in your browser to navigate the documentation.

The present code assumes you already have a Solr core set up which indexes your pre-processed data. The code to run this 
pre-processing and create the Solr core are contained in the "preprocessing" sub-folder at the root of this repository. 
Assuming that this data is Twitter (X) data, here are the fields that are expected to be indexed in Solr by the current 
project: 

|   **Field name**  |   **Type**  |                               **Description**                              |
|:-----------------:|:-----------:|:--------------------------------------------------------------------------:|
| id                | str         | Tweet ID                                                                   |
| fullText         | str         | Original tweet text (no pre-processing)                                    |
| createdAtDays   | str         | Day tweet was published in YYYY-MM-DD format                               |
| userScreenName  | str         | Username of author on Twitter                                              |
| usersDescription | str         | Twitter biography of author, written by themselves                         |
| locationGps      | str         | GPS location of tweet (declared by author)                                 |
| userLocation     | str         | GPS location of author (declared by author)                                |
| processedTokens  | list[str]   | Tweet's tokens after pre-processing: i.e. stopwords removal, lemmatisation |
| retweetCount     | int         | Number of times tweet was retweeted in total                               |
| language          | str         | Language the tweet is written in (e.g. "English")                          |
| sentiment         | str         | Sentiment of tweet, must be one of "Positive", "Neutral" or "Negative"     |
| embedding_5d      | list[float] | 5-dimensional embedding representation of tweet                            |
| embedding_2d      | list[float] | 5-dimensional embedding representation of tweet                            |

The *language* field is obtained by running a language detection model on the data, *sentiment* by running a sentiment 
analysis classifier, and *embedding_5d* and *embedding_2d* by running first the SBERT language model to obtain a large 
embedding represention and then running the UMAP algorithm to reduce the dimensions of these embeddings to 5 and then 2 
dimensions.

Once the Solr cores are set up with the correct fields indexed, you can follow the following steps to run the dashboard 
on your local machine.

## Setting up project on local machine for development

To set up the project after cloning the repository:

1) Modify the *SOLR_URL*, *SOLR_PORT* and *SOLR_CORES* fields in fantom-ui/api/configs.py file to point to your own Solr set up.

2) Install Javascript dependencies:
```
cd dashboard
yarn install
```

3) Create Python virtual environment and install dependencies:
```
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4) Launch React app:
```
cd ..       # you should be at the root of the dashboard folder once again
yarn start
```

5) Launch Flask back-end in a new terminal:
```
cd dashboard
yarn start-api
```

6) Access the app from http://localhost:3000/ in your browser

