# TwiXplorer PreProcessing Modules

## Description

This repository contains the preprocessing modules for the TwiXplorer analysis tool.
It contains the following modules:

## Table of Contents
* [Installing Conda environment](#installingConda)
* [Set Evironment Variables](#settingEnv)
* [Managing Solr](#managingSolr)
* [Adding Data to Solr](#addingDataToSolr)
    * [Data extraction](#extractTweetFromFile)
    * [Adding data to Solr](#addingProcessedDataToSolr)
* [Process Locations](#location)
    * [Start the Location Service API](#runLocationAPI)
    * [Start the Location Process](#runLocationProcessor)
* [Process Sentiments](#sentiment)
    * [Start the Sentiment Service API](#runSentimentAPI)
    * [Start the Sentiment Process](#runSentimentProcessor)
* [Process Embeddings Module](#processEmbeddingsModule)
    * [Extracting the text data from Solr](#embeddingsExtractingText)
    * [Generate sentence embeddings](#embeddingsGenerateEmbeddings)
    * [Reduce the dimensionality to 5d](#embeddingsReduceTo5D)
    * [Reduce the dimensionality to 2d](#embeddingsReduceTo2D)
    * [Update Solr with the embeddings](#embeddingsAddToSolr)
* [Process SNA](#processSNA)
    * [Extracting the network data from Solr](#SNAExtractNetwork)
    * [Process Network](#SNAProcessNetwork)
    * [Import Network Data To Solr](#SNAimportNetworkToSolr)

    
## Installation

### <a id="installingConda">1. Installing Conda environment</a>:

Each module has its own set of dependencies. However, all of these libraries can be installed by the following prompt
command:

To create a virtual environment (<i><b>run this one time only</b></i>):

```
conda create -n venv python=3.8.19
```

and after the installation completed (<i><b>run this every time you start any of the backend sessions</b></i>):

```
conda activate venv
```

For more details about the previous two steps please
visit [Managing environments from Conda](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#). (internet required).

Next, you need to install the libraries (<i><b>internet required</b></i>) (<i><b>run this one time only</b></i>):

```
pip install -r requirements.txt
```

For MacOS systems, please install the required libraries by the following command:
```
pip install -r requirements-macOS.txt
```


### <a id="settingEnv">2. Generate the required keys</a>
This is an important step to be performed before starting the backend processing and the front end backend and ui processes.
By running the generate_codes command from the narrative-backend root folder as shown below (<i><b>required to be run one time only</b></i>):

```
python generate_codes.py 
``` 

### <a id="managingSolr">3. Apache Solr.<a>

For detailed information on how to download and start solr, please read [Solr ReadMe.md](/preprocessing/solr/README.md) file.
You can start Solr instance from the downloaded Solr, but we suggest to start it from solr folder in this repo. Adding
the core is mandatory to be from ths solr controller to have the core initiated with the required fields.


### <a id="addingDataToSolr">4. Adding tweets to the Apache Solr instance</a>

#### <a id="extractTweetFromFile"> - Extracting Tweets from Raw Data:</a>
If you have the raw X (Twitter) data stored in a set of files within a folder `.sample_dats` , you can extract the features by running the command (<i><b>No internet required</b></i>) but (<b><i> required evey time new data added to the folder</b></i>):

```
python 1_extract_data.py -s ../.sample_data/
```

Make sure to run the command prompt from the folder: ```/twixplorer/preprocessing/data_updater/``` 

The output of this step will be stored in the folder `../.sample_data_processed/` 

#### <a id="addingProcessedDataToSolr">- Adding Processed Data to Solr:</a>
Next, from the same folder (```/twixplorer/preprocessing/data_updater/```), run the following Python code:
```
python 2_import_data_to_solr.py -c _new_core -s ../.sample_data_processed/
```

### <a id="location">5. Processing the Location details</a>

We have two steps for this process:

1- <a id="runLocationAPI">Run the location-api</a>
    To run the api, simply execute the shell script `./1_location_run.sh` in the folder (`/twixplorer/preprocessing/location_api`). 

2- <a id="runLocationProcessor">Process the locations</a>
    After running the location api, process the locations by running the following command from the folder  ```/twixplorer/preprocessing/data_updater/```

```
python 3_update_locations.py -c new_core
```
Or simply, the shell script ```run_location_updater.sh``` from the data_updater after updating the core name in the shell script file.

### <a id="sentiment"> 6. Processing the Sentiments details</a>

Two steps:

#### <a id="runSentimentAPI">1- Run the sentiment-api (<i><b>requires internet access</b></i>)</a>.

To run the api, simply execute the shell script `./1_sentiment_run.sh` in the `/twixplorer/preprocessing/sentiment_api/` folder. It requires to download the Sentiment analysis model from Hugging Face. [Click here for more details about the utilized model](https://huggingface.co/cardiffnlp/twitter-xlm-roberta-base-sentiment). After running the service, you can disconnect the internet.

#### <a id="runSentimentProcessor">2- Process the sentiments</a>
After running the sentiment analysis api, process the sentiments by running the following command from the folder  ```/twixplorer/preprocessing/data_updater/```

```
python 4_update_sentiments.py -c new_core
```
Or simply, the shell script ```run_sentiment_updater.sh```

### <a id="processEmbeddingsModule">7. Embeddings Module</a>
Topic modelling embeddings must be stored in Solr to run this feature in the analysis. These steps are listed with an explanation on how to run them as follow:

1-	<a id="embeddingsExtractingText">Extracting the text data from Solr</a> `python extract_text_data.py`,

2-	<a id="embeddingsGenerateEmbeddings"> Generate sentence embeddings</a> `python 2_generate_sentence_embeddings.py`

3-	<a id="embeddingsReduceTo5D">Reduce the dimensionality to 5d</a> `python 3_reduce_to_5d.py`

4-	<a id="embeddingsReduceTo2D">Reduce the dimensionality to 2d</a> `python 4_reduce_to_2d.py`

5-	<a id="embeddingsAddToSolr">Update Solr with the embeddings</a> `python 5_import_embeddings_to_solr.py -c core_name`

These command must be done in the listed order. The output of one step might be an input for the consecutive ones.

#### NOTE: After finishing these steps, two folders will be created in the folder "sentence_embeddings". TwiXplorer's dashboard requires these two folders to load the models. In case you got failure due to not having these two folders in the desired location, please perform the following:

- Make sure that the folders are generated successfully.
- Make sure that the paths of these folders are correctly set in the file topic_modelling_utils.py from the TwiXplorer's dashboard folder.


### <a id="processSNA"> 8. Social Network Analysis (SNA) Module</a>


- <a id="SNAExtractNetwork"> **Extract Network Information**</a>


Firstly, you need to extract the network information from Solr, to perform that, you can run the following Python code: 

```
python 1_extract_network_from_solr.py -c new_core
```

Next you need to use the output file, by default it is `/twixplorer/preprocessing/network_interaction/data/df_data_new_core.csv`  in as an input for the Java program to build the SNA graph. 

**NOTE: you can skip this step**, we add this to show how to create the Java classes by using the following commands (you can skip this step as the Java classes are provided already):

```
javac -cp •/gephi-toolkit-0.10.0-all.jar Main.java GephiVis.java
```
**Ending the optional step**

- <a id="SNAProcessNetwork"> **Process the Extracted Network**</a>

Now, you need to run the program from the classes already generated and pass the extracted network data from the step above:

```
java -cp .:./gephi-toolkit-0.10.0-all.jar Main 10 ./data/df_data_new_core.csv
```
In this command, we limited the process timeout to 10 minutes, which depends on the network size. This is by setting the parameter 10 after the parameter (Main). 
We usually set it to 60 minutes for a reasonable network graph. You can check that configuration from the shell script ./2_generate_graph.sh in the network_interaction folder.
The output of this program will be written to the file, ```/twixplorer/preprocessing/network_interaction//data/df_data_GRAPH.json```. 

To simplify this step, we added a shell script (2_generate_graph.sh), but you only need to run it once.

- <a id="SNAimportNetworkToSolr"> **Import Network Data to Solr**</a>
Next you need to import this data into Solr by using the following command:

```
python import_networks_to_solr.py -c new_core -s ./data/df_data_GRAPH.json
```


## Credits:

### [Gephi](https://gephi.org) 
Bastian M., Heymann S., Jacomy M. (2009). Gephi: an open source software for exploring and manipulating networks. International AAAI Conference on Weblogs and Social Media.



(c) Turing Innovations Limited: folders network_interaction, sentence_embeddings

(c) The University of Edinburgh: folders data_updater, location_api, sentiment_api, solr
