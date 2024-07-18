# TwiXplorer: An Interactive Tool for Narrative Detection and Analysis in Historic Twitter Data

Welcome to TwiXplorer, an interactive tool to explore and understand static Twitter (X) datasets! Our system is 
advanced and easy to use and demonstrates how AI can help and be integrated into a process to make sense of large 
datasets. The tool is accessed through a web-based dashboard and designed with interaction in mind: the analyst can 
iteratively explore the data instead of being presented with static reports.

If you decide to use our tool, please cite our paper: 

[TODO: ADD PAPER CITATION]

## Features

[TODO: add screenshots for each feature]


## Repository structure

This repository is composed of the following folders: 

* **pre-processing**: Contains the code to pre-process your Twitter (X) data and load it into the tool.
* **dashboard**: Contains the code to run the React front-end and Flask back-end for the dashboard. 

## Getting started

To set up the project after cloning the repository, follow the following two steps: 

1. **Run data pre-processing**: Go into the "preprocessing" sub-folder and follow the instructions in the README file. 
This will allow you to pre-process your Twitter (X) dataset and load it into a Solr core for future use in the dashboard. 
2. **Launch dashboard**: Go into the "preprocessing" sub-folder and follow the instructions in this second README file.

The **twixplorer-ui** folder itself contains the following two sub-folders:

* **api**: Contains the code of the Flask back-end. 
* **src**: contains the code of the React front-end.

The **docs** sub-folder inside **api** contains the HTML documentation for this API. You can download the docs folder and then open the file _build/html/index.html in your browser to navigate the documentation.


