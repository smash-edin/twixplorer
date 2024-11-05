# TwiXplorer Dashboard

This repository is composed of the following sub-folders: 

* **api**: Contains the code of the Flask back-end of the TwiXplorer dashboard. 
* **src**: contains the code of the React front-end of the TwiXplorer dashboard.

The present code assumes you already have a Solr core set up which indexes your pre-processed data (from following the 
instructions inside the twixplorer/preprocessing folder). Assuming that this data is Twitter data, here are the fields 
that are expected to be indexed in Solr by the current project: 

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

## Launching TwiXplorer dashboard

Once the Solr cores are set up with the correct fields indexed, you can follow the following steps to run the dashboard 
on your local machine.

To set up the project after cloning the repository:

1) Modify the *SOLR_URL*, *SOLR_PORT*, *SOLR_CORES*, *SA_ULR* and *LOCATION_URL* fields in dashboard/api/configs.py 
file to point to your own Solr set up.

2) Go to dashboard/src/.data/datasetOptions.csv and add the list of Solr core names you want to be able to select 
inside the dashboard.

3) Install Javascript dependencies:
```
cd dashboard
yarn install
```
Note that this might not work if yarn is not installed, in which case follow the instructions from the following webpage: [https://classic.yarnpkg.com/lang/en/docs/install](https://classic.yarnpkg.com/lang/en/docs/install)

4) Create Python virtual environment and install dependencies (<i><b>internet access required</b></i>):
```
cd api
python3.8 -m venv venv
source venv/bin/activate
```

In case the installation failed, the error message may suggest a solution such as installing the messing package. However, it may require root access to install the required package.

If the error is related to the Python 3.8 version, you can try the following solution, assuming that the narratives-backend installation steps have already been performed in the system (<i><b>internet access required</b></i>):

```
cd api
conda activate venv
pip install virtualenv
virtualenv -p $(which python3.8) venv
conda deactivate
source venv/bin/activate
```

After activating the virtual environment, we need to install the requirements by firing the following (<i><b>internet access required</b></i>):

```
pip install -r requirements.txt
```

Please notice that this must be performed only once.

After having the virtual environment install correctly, you can perform the following:

```
cd api
source venv/bin/activate
```
and the system is ready to be used as shown in the following steps.


5) Launch React app:
```
cd ..       # you should be at the root of the dashboard folder
yarn start
```

6) Launch Flask back-end in a new terminal:
```
cd dashboard
yarn start-api
```

7) Access the app from http://localhost:3000/ in your browser

**Optional**: You can decide to run the Flask API and React front-end on separate machines. If so, you need to go to the 
following files and make the appropriate modifications where flagged: 
- dashboard/config/allowedOrigins.js
- dashboard/src/api/axios.js

