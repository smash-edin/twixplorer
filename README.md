# TwiXplorer: An Interactive Tool for Narrative Detection and Analysis in Historic Twitter Data

Welcome to TwiXplorer, an interactive tool to explore and understand static Twitter (X) datasets! Our system is 
advanced and easy to use and demonstrates how AI can help and be integrated into a process to make sense of large 
datasets. The tool is accessed through a web-based dashboard and designed with interaction in mind: the analyst can 
iteratively explore the data instead of being presented with static reports.

If you decide to use our tool, please cite our paper: 

Al Hariri, Youssef, Sandrine Chausson, Björn Ross, and Walid Magdy. "TwiXplorer: An Interactive Tool for Narrative Detection and Analysis in Historic Twitter Data." In Companion Publication of the 2024 Conference on Computer-Supported Cooperative Work and Social Computing, pp. 83-86. 2024.

## Features

1) Input header

![Demo_CSCW](https://github.com/user-attachments/assets/2b7d7c3e-7ed7-4c19-8472-efdc65c19301)


2) Timeline

3) Sentiment


You can also watch a video demo of our tool here: https://dl.acm.org/doi/abs/10.1145/3678884.3681815 


## Repository structure

This repository is composed of the following folders: 

* **pre-processing**: Contains the code to pre-process your Twitter (X) data and load it into the tool.
* **dashboard**: Contains the code to run the React front-end and Flask back-end for the dashboard. 

## Getting started

To set up the project after cloning the repository, follow the following two steps: 

1. **Run data pre-processing**: Go into the "preprocessing" sub-folder and follow the instructions in the README file. 
This will allow you to pre-process your Twitter (X) dataset and load it into a Solr core for future use in the dashboard. 
2. **Launch dashboard**: Go into the "preprocessing" sub-folder and follow the instructions in this second README file.


