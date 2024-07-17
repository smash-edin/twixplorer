# TwiXplorer: An Interactive Tool for Narrative Detection and Analysis in Historic Twitter Data

Welcome to TwiXplorer, an interactive tool to explore and understand static Twitter (X) datasets! Our system is more advanced and easy to use than existing options and demonstrates how AI can help and be integrated into a process to make sense of large datasets. The tool is accessed through a web-based dashboard and designed with interaction in mind: the analyst can iteratively explore the data instead of being presented with static reports. We make the tool fully open source.

If you decide to use our tool, please cite our paper: 

[TODO: ADD PAPER CITATION]

## Getting started

To set up the project after cloning the repository:

[TODO: Add pre-processing steps]

1) Modify the *SOLR_URL*, *SOLR_PORT* and *SOLR_CORES* fields in twixplorer/twixplorer-ui/api/configs.py file to point to your own Solr set up.

2) Install Javascript dependencies:
```
cd twixplorer-ui
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
cd ..       # you should be in the twixplorer-ui folder once again
yarn start
```

5) Launch Flask back-end in a new terminal:
```
cd twixplorer-ui
yarn start-api
```

6) Access the app from http://localhost:3000/ in your browser

## Repository structure

This repository is composed of the following folders: 

* **twixplorer-backend**: Contains the pre-processing code to pre-process your Twitter (X) data and load it into the tool.
* **twixplorer-ui**: Contains the code to run the React front-end and Flask back-end for the dashboard. 

The **twixplorer-ui** folder itself contains the following two sub-folders:

* **api**: Contains the code of the Flask back-end. 
* **src**: contains the code of the React front-end.

The **docs** sub-folder inside **api** contains the HTML documentation for this API. You can download the docs folder and then open the file _build/html/index.html in your browser to navigate the documentation.

## Data fields requirements

The present code assumes you already have a Solr core set up which indexes your pre-processed data. We will publish consolidated code to run this pre-processing and create the Solr core in a future release. Assuming that this data is Twitter data, here are the fields that are expected to be indexed in Solr by the current project: 

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

The *language* field is obtained by running a language detection model on the data, *sentiment* by running a sentiment analysis classifier, and *embedding_5d* and *embedding_2d* by running first the SBERT language model to obtain a large embedding represention and then running the UMAP algorithm to reduce the dimensions of these embeddings to 5 and then 2 dimensions.

Once the Solr cores are set up with the correct fields indexed, you can follow the following steps to run the dashboard on your local machine.
