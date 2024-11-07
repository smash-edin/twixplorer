# PreProcessing - Apache Solr Instance Controller Module

## Description

This folder contains a simple controller to control the Apache Solr Platform for the usage in the TwiXplorer
tool from the project Modelling Audience Interactions.

## Downloading Apache Solr:

Download the Solr from [Solr Apache](https://solr.apache.org/downloads.html).

The system is intensively tested with [Solr 9.3.0](https://archive.apache.org/dist/solr/solr/9.3.0/).

## Installing Solr

After downloading Solr, decompress the file in a folder of your choice. It is not mandatory to be within the
preprocessing folder. After that please follow the following steps carefully:

1. Update the file _**./solr_path/bin/solr.in.sh**_ for server running with Linux/Max OS, (_or_
   _**./solr_path/bin/solr.in.cmd**_ for servers with Microsoft OS) with the following settings:
    1. For a scalable usage of Solr:
        1. comment the line that has the value SOLR_HEAP. It should be as following:
       ```
       #SOLR_HEAP=
       ```
        2. Uncomment the line with the constant SOLR_JAVA_MEM and set it with the following parameters in case the data
           is extremely large make it as follow:
       ```
       SOLR_JAVA_MEM="-Xms10g -Xmx20g"
       ```

    2. Set the SOLR_PORT to the desired port number. An example:
   ```
   SOLR_PORT=10196
   ```
    3. This step is important to keep your system secure. However, it requires further knowledge in the network. You need to know the IP address of the allowed devices to access Solr. Add the urls of the host(s) of both Solr and the TwiXplorer-backed system  to the SOLR_IP_ALLOWLIST as follow:
   ```
   SOLR_IP_ALLOWLIST=127.0.0.1
   ```
   In case you face any difficulty in accessing Solr, then comment the line to test Solr is up and accessible.



    4. Set SOLR_JETTY_HOST setting. For security, you may consider running the Solr of the same server that runs other
       modules and keep the SOLR_JETTY_HOST=127.0.0.1. If security is not concern, then you may consider making it SOLR_JETTY_HOST=0.0.0.0 or even commenting this value to be:
       #SOLR_JETTY_HOST=127.0.0.1

    5. Uncommend the autoCommit lines, 
    ```
    SOLR_OPTS="$SOLR_OPTS -Dsolr.autoSoftCommit.maxTime=3000"
    SOLR_OPTS="$SOLR_OPTS -Dsolr.autoCommit.maxTime=60000" 
    ```

    6. Save the **_solr.in.sh_** (or **_solr.in.cmd_**) file.


2. Update the **_configs.py_** file in the folder **_data_updater_** with the port number you specified in the
   ApplicationConfig (Make sure that the attributes **SOLR_PORT**, **SOLR_PATH** and **SOLR_URL** hold the correct
   values).


3. To start Solr, from the solr folder in this repository, run the following command:
   ```
   python solr_controller.py -d start
   ```

   If the error message "Port is already being used" printed, then check if another service uses the port number you
   identified above, or if Solr is already running with this Port.


4. To create a new collection, aka core, run the following command:

   ```
   python solr_controller.py -d add -c new_core
   ```
   The expected result is: Created new core 'new_core'. In case the core is already created, the error
   message "Core 'new_core' already exists!". You need to check the available cores.

   After creating the Solr core, you need to update ApplicationConfig.SOLR_CORES so it includes the name of the new
   core.

   Note: although deleting the core and starting Solr might be performed directly through Solr interface, creating
   the core should be done by this tool to initiate the required fields in the schema file. Otherwise, the system might
   not work as expected.


5. To delete the already exist core (**_CAUTION_**: this process is non-reversible and will remove the core
   permanently):
   ```
   python solr_controller.py -d delete -c new_core
   ```
   The expected message is "The collection has been deleted successfully, please update the configs.py file
   accordingly.". However, if the core does not exist or the port/path settings have inaccurate details you may get the
   error message: "Cannot unload non-existent core".


