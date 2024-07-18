# TwiXplorer Project PreProcessing Modules

## Description

This repository contains the preprocessing modules for the narratives analysis tool from the project Modelling Audience
Interactions.
It contains the following modules:

## Table of Contents

* [Installation](#installation)
* [Usage](#usage)
* [Credits](#credits)
* [License](#license)

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

## Usage 