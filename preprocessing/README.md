# TwiXplorer PreProcessing Modules

## Description

This repository contains the preprocessing modules for the TwiXplorer analysis tool.
It contains the following modules:

## Table of Contents

* [Installation](#installation)



## Installation

### 1. Installing Conda environment:

Each module has its own set of dependencies. However, all of these libraries can be installed by the following prompt
command:

To create a virtual environment:

```
conda create -n venv python=3.8.18
```

and after the installation completed:

```
conda activate venv
```

For more details about the previous two steps please
visit [Managing environments from Conda](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#).

Next, you need to install the libraries:

```
$ pip install -r requirements.txt
```

### 2. Apache Solr.

For detailed information on how to download and start solr, please read [Solr ReadMe.md](/solr/README.md) file.
You can start Solr instance from the downloaded Solr, but we suggest to start it from solr folder in this repo. Adding
the core is mandatory to be from ths solr controller to have the core initiated with the required fields.

### 3. Generate the required keys
By running the shel script generate_code.sh in the preprocessing root folder.

### 4. Adding tweets to the Apache Solr instance

If you have the raw X (Twitter) data stored in a set of files within a folder `.sample_dats` , you can extract the features by running the command:

```
python 1_extract_data.py -s ../.sample_data/
```

while the command prompt is at the folder: ```/preprocessing/data_updater/``` 

The output of this step will e stored in the folder `../.sample_data_processed/` 
Next, from the same folder, run the Python code:
```
python 2_import_data_to_solr.py -c _new_core -s ../.sample_data_processed/
```

### 5. Processing the Location details

Two steps:
1- Run the location-api
    To run the api, simply execute the shell script `./1_location_run.sh` in the `preprocessing/location_api` folder. 
2- Process the locations
    After running the location api, process the locations by running the following command from the folder  ```/preprocessing/data_updater/```

```
python 3_update_locations.py -c new_core
```
Or simply, the shell script ```run_location_updater.sh```
### 6. Processing the Sentiments details

Two steps:
1- Run the sentiment-api
To run the api, simply execute the shell script `./1_sentiment_run.sh` in the `preprocessing/sentiment_api/` folder.
2- Process the sentiments
After running the sentiment analysis api, process the sentiments by running the following command from the folder  ```/preprocessing/data_updater/```

```
python 4_update_sentiments.py -c new_core
```
Or simply, the shell script ```run_sentiment_updater.sh```

### 7. Embeddings Module
Topic modelling embeddings must be stored in Solr to run this feature in the analysis. These steps are:
1-	Extracting the text data from Solr `python extract_text_data.py`,
2-	Generate sentence embeddings `python 2_generate_sentence_embeddings.py`
3-	Reduce the dimensionality to 5d `python 3_reduce_to_5d.py`
4-	Reduce the dimensionality to 2d `python 4_reduce_to_2d.py`
5-	Update Solr with the embeddings `python 5_import_embeddings_to_solr.py -c core_name`

These can be run by using the commands


### 8. Social Network Analysis (SNA) Module

Firstly, you need to extract the network information from Solr, to perform that, you can run the following Python code: 

```
/preprocessing/network_interaction$ python 1_extract_network_from_solr.py -c new_core
```

Next you need to use the output file, by default it is `/preprocessing/network_interaction/data/df_data_new_core.csv`  in as an input for the Java program to build the SNA graph. 

It is possible to skip the following step, but you can create the Java classes by using the following commands (you can skip this step as the Java classes are provided already):

```
/preprocessing/network_interaction$ javac -cp •/gephi-toolkit-0.10.0-all.jar Main.java GephiVis.java
```

After that, you can run the program from the classes already generated and pass the extracted network data from the step above:

```
/preprocessing/network_interaction$ java -cp .:./gephi-toolkit-0.10.0-all.jar Main 10 ./data/df_data_new_core.csv
```
The output of this program will be written to the file, ```/preprocessing/network_interaction//data/df_data_GRAPH.json```. Next you need to import this data into Solr by using the following command:

```
/preprocessing/network_interaction$ python import_networks_to_solr.py -c new_core -s ./data/df_data_GRAPH.json
```


## Credits:

### [Gephi](https://gephi.org) 
Bastian M., Heymann S., Jacomy M. (2009). Gephi: an open source software for exploring and manipulating networks. International AAAI Conference on Weblogs and Social Media.



(c) Turing Innovations Limited: folders network_interaction, sentence_embeddings

(c) The University of Edinburgh: folders data_updater, location_api, sentiment_api, solr
