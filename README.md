# TwiXplorer: An Interactive Tool for Narrative Detection and Analysis in Historic Twitter Data

Welcome to TwiXplorer, an interactive tool to explore and understand static Twitter (X) datasets! Our system is 
advanced and easy to use and demonstrates how AI can help and be integrated into a process to make sense of large 
datasets. The tool is accessed through a web-based dashboard and designed with interaction in mind: the analyst can 
iteratively explore the data instead of being presented with static reports.

If you decide to use our tool, please cite our paper: 

Al Hariri, Youssef, Sandrine Chausson, Björn Ross, and Walid Magdy. "TwiXplorer: An Interactive Tool for Narrative Detection and Analysis in Historic Twitter Data." In Companion Publication of the 2024 Conference on Computer-Supported Cooperative Work and Social Computing, pp. 83-86. 2024.

## Repository structure

This repository is composed of the following folders: 

* **pre-processing**: Contains the code to pre-process your Twitter (X) data and load it into the tool.
* **dashboard**: Contains the code to run the React front-end and Flask back-end for the dashboard. 

## Getting started

To set up the project after cloning the repository, follow the following two steps: 

1. **Run data pre-processing**: Go into the "preprocessing" sub-folder and follow the instructions in the README file. 
This will allow you to pre-process your Twitter (X) dataset and load it into a Solr core for future use in the dashboard. 
2. **Launch dashboard**: Go into the "preprocessing" sub-folder and follow the instructions in this second README file.

## Features

### 1) Input header

The input header allows the analyst to specify the data in which they would like to discover narratives. A dataset must be selected. All other fields are optional filters: leave all of them empty to generate an analysis of the entire dataset, or specify some to narrow down your search.

<div align="center">
  <img src="https://github.com/user-attachments/assets/b138d5ff-44cf-4a96-acd3-c9c4b2f720dc" alt="header" width="600">
</div>

### 2) Timeline

The timeline component shows the volume of data per day matching the search filters. If more than one keyword was provided, a different line is plotted for each keyword as well as for all keywords together ("Any keyword"/"All keywords").

<div align="center">
  <img src="https://github.com/user-attachments/assets/3a5aac5a-9a0b-4895-98be-7cce9e6ba5fa" alt="timeline" width="600">
</div>
   
### 3) Sentiments

The Sentiment component shows the break down of the data per sentiment. Click on a sentiment in the legend to hide/show it on the visualisation, and double-click on it to make it the only visible sentiment.

<div align="center">
  <img src="https://github.com/user-attachments/assets/87238b28-62ef-472a-bb12-d7f64b8ebaba" alt="sentiment" width="600">
</div>

### 4) Languages

The Language component shows the volume of data per language. If the dataset only contains one language, a single bar will be shown in the graph.
   
<div align="center">
  <img src="https://github.com/user-attachments/assets/26edb2bb-bcde-4413-9aa2-aedcca86024c" alt="languages" width="600">
</div>

### 5) Location

The Map component shows the break down of the data according to the geographical location of users or tweets.
   
<div align="center">
  <img src="https://github.com/user-attachments/assets/ce509e29-a80d-44ab-a9b4-a0538c6b3ec3" alt="location" width="600">
</div>

### 6) Top Content

The Top Content component shows the most retweeted tweets, users, URLs, media and emojis in the current search. By default, results are shown in groups of 5. You can navigate to the next page of results by clicking on arrows at the bottom right of the table.
   
<div align="center">
  <img src="https://github.com/user-attachments/assets/4757a23c-d1bb-4517-9097-05e0f12875cb" alt="top_content" width="600">
</div>

### 7) Wordclouds

The Wordcloud component shows the most frequent words or emojis in the data in the form of a wordcloud. Clicking on any word or emoji will generate a new report (in a new tab), where the clicked word/emoji will have been appended to the current keyword(s).
   
<div align="center">
  <img src="https://github.com/user-attachments/assets/d106320f-d860-4dc9-802f-e6772772adf6" alt="wordclouds" width="600">
</div>


### 8) Topic Discovery

   a. Visualisation of tweets in semantic space

The Topic Discovery components allows the user to visualise the data from the current search in semantic space: i.e. tweets that are semantically similar are located close to each other. Tweets are represented as dots in the visualisation. Hovering over a dot will display the tweet. Clicking on a datapoint will open the tweet on Twitter (X) in a new tab.
   
<div align="center">
  <img src="https://github.com/user-attachments/assets/97261329-fdd9-42c5-a20d-d9f07851375a" alt="topics_vis" width="600">
</div>


   b. Worldclouds from topics

Once the Topic Discovery is generated with a number of topics greater than 0, the "Topics" option appears under the "Field" menu of the Wordclouds feature. This allows the analysts to see the most common terms in the text of tweets that compose each topic. The "Topic" menu then allows the analyst to choose the topic they want to see a wordcloud for.

<div align="center">
  <img src="https://github.com/user-attachments/assets/e30537f1-6bd8-4728-a88a-19993ca69c93" alt="wordclouds_topics" width="600">
</div>


### 9) Social Network Analysis

    a. Visualisation of users' proximity based on retweets

The Social Network Analysis components allows the user to visualise the "proximity" between authors of tweets contained in the current search search, as measured by the number of times users have retweeted each other in the dataset: i.e. users that retweet each other a lot are located closer to each other while those who don't are located further apart. This component also shows the community each user belongs to as inferred from their retweets in the overall dataset. Users are represented as dots in the visualisation. Hovering over a dot will display the user's description (if available) as well as the community number. Clicking on a datapoint will open the user's profile on Twitter (X) in a new tab. Moreover, the "Tweeting per community" component shows the number of tweets posted over time by each of the communities highlighted in the Social Network Analysis visualisation. The "Communities stats" component, on the other hand, shows statistics for each community. These include the number of accounts in the community for the current search, the average number of tweets per account, the average number of retweets per tweet and the screen name of the 10 most retweeted accounts in the community. Clicking on a user screen name will open the user profile on Twitter (X) in a new tab.
   
<div align="center">
  <img src="https://github.com/user-attachments/assets/99e3c438-a9e8-44fb-b104-39b2778a5035" alt="sna_vis" width="600">
</div>

    b. Worldclouds from user descriptions

Once the Social Network Analysis is generated, the "Community user descriptions" option appears under the "Field" menu of the Wordclouds feature. This allows the analysts to see the most common terms in the user descriptions of users belonging to each community. The "Community" menu then allows the analyst to choose the community they want to see a wordcloud for.
   
<div align="center">
  <img src="https://github.com/user-attachments/assets/fc162ff8-9132-41e0-a6d7-42353fa26da1" alt="wordclouds_sna" width="600">
</div>

For more information, feel free to watch a video demo of TwiXplorer here: https://dl.acm.org/doi/abs/10.1145/3678884.3681815  


