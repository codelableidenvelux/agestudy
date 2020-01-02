# Agestudy
This repository contains the code for the Agestudy website.
Agestudy contains 3 cognitive tasks and 2 surveys implemented in Psytoolkit.
This README contains information on the structure of this repository.

## Repository overview
├──Nested =  This indicates there is a file inside a folder  
<pre>
├── requirements.txt   <- The requirements file for reproducing the analysis
├── app                <- Source code for the web application     
│   ├── templates           <- Contains all the html scripts
│   ├── static           <- Contains css, js and images
│   │     ├── css  <- contains all the css scripts
│   │     │                
│   │     ├── images  <- contains images used on the website including favicon
│   │     │     
│   │     └── js  <- contains javascript code
│   │     
│   ├── db        <- Contains all the information for the database
│   │     ├── python_2_db2.py  <- talk to db2 with python
│   │     │                
│   │     ├── tables.sql  <- SQL script to make all the tables
│   │     │     
│   │     ├── delete.sql  <- SQL drop tables
│   │     │     
│   │     └── test.sql  <- insert some data in the tables to test them
│   │
│   ├── application.py      <-- application to run the website
│   ├── helpers.py          <-- functions to use in application.py
│   └── localserver_run     <-- run the application locally
├────────────────────────────────────────────────────────────────────────────────────
│              
├── psychtoolkit        <- Contains psychtoolkit scripts
│   │
│   ├── corsi           <- Contains all the scripts and bitmaps for corsi
│   │     └── corsi_bitmaps          <- contains all the bitmaps used for corsi
│   │
│   ├── n_back           <- Contains all the scripts and bitmaps for n-back
│   │     └── n_back_bitmaps      <- contains all the bitmaps used for N-back
│   │
│   ├── task_switch       <- Contains all the scripts and bitmaps for task switching
│   │     └── task_switch_bitmaps    <- contains all the bitmaps used for task_switch
│   │
│   ├── Phone_survey       <- Contains the script and images for the phone survey       
│   │     └── images    <- contains all the hands images
│   │
│   ├── SF-36      <- Contains the script for the SF-36
│   ├── Feedback     <- Contains the script for the feedback survey
├────────────────────────────────────────────────────────────────────────────────────
├── data_processing   <- Contains basic data_cleaning and processing scripts
├────────────────────────────────────────────────────────────────────────────────────
├── reports   <- Contains files such as feedback or powerpoints
</pre>
## Sources

## Author(s)
Ruchella Kock :cat:

Codelableiden - Leiden University
