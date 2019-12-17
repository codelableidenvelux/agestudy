# Psytoolkit experiments and surveys
This folder contains information for all the psychological tasks used on psytoolkit.
This README contains a detailed overview of the files in this folder.

# Experiment and Survey set up
## Get started
Create an account on [Psytoolkit](https://www.psytoolkit.org/#_web_based_login)
Login and click on *create survey*, choose a survey name.
Create a blank (survey)[https://www.psytoolkit.org/doc2.6.1/online-survey-intro.html#_how_to_create_a_survey] on Psytoolkit
Paste the script from the *name_survey.txt* file into the the blank survey
![Create survey]("instruction_images/create_survey.png")

Click on *create experiment*, choose method 1 (completely new experiment) and choose an experiment name.
Create a blank (experiment)[https://www.psytoolkit.org/lessons/project.html] on Psytoolkit
Paste the script from the *name_experiment.txt* file into the the blank experiment
![Create survey]("instruction_images/create_experiment.png")

# Bitmaps
Each folder contains a set of bitmaps that need to be added to the experiment.
Go to the experiment, click on choose files and upload all the files.
Note: DO NOT change the names of the images!
[Read more on bitmaps](https://www.psytoolkit.org/lessons/show_bitmaps.html)

## Settings
In every folder for each task there is a README file with information about the settings for the experiments.
All the experiments have started out as sample experiments from the psytoolkit experiment library. In each README.md file for each task there is a link to the experiment in the library.
These individual README files also contain the structure of the data that is being collected.
For a broad overview of the data collected see : https://github.com/codelableidenvelux/agestudy/tree/master/reports/data_structure.docx

# Folder Overview
<pre>
│              
├── psychtoolkit        <- Contains psychtoolkit scripts
│   │
│   ├── corsi           <- Contains all the scripts and bitmaps for corsi
│   │     │     
│   │     ├── README.md  <- contains all the information about corsi and
│   │     │                 special selections. Including data structure.
│   │     ├── corsi_experiment.txt  <- script for the experiment
│   │     │     
│   │     ├── corsi_survey.txt  <- script for the survey to run corsi
│   │     │    
│   │     │     
│   │     └── corsi_bitmaps          <- contains all the bitmaps used for corsi
│   │
│   ├── Feedback     <- Contains the script for the feedback survey
│   │     │     
│   │     ├── README.md  <- contains all the information about the feedback survey &
│   │     │                 special selections. Including data structure.
│   │     │     
│   │     └──feedback.txt  <- survey script
│   ├── n_back           <- Contains all the scripts and bitmaps for n-back
│   │     │     
│   │     ├── README.md  <- contains all the information about n-back and
│   │     │                 special selections. Including data structure.
│   │     │     
│   │     ├── n_back_experiment.txt  <- script for the experiment
│   │     │     
│   │     ├── n_back_survey.txt  <- script for the survey to run N-back
│   │     │     
│   │     │     
│   │     └── n_back_bitmaps      <- contains all the bitmaps used for N-back
│   │
│   ├── Phone_survey       <- Contains the script and images for the phone survey
│   │     │     
│   │     ├── README.md  <- contains all the information about the phone survey and
│   │     │                 special selections. Including data structure.
│   │     │     
│   │     ├── phone_survey_english.txt  <- survey script
│   │     │     
│   │     ├── phone_survey_dutch.txt  <- survey script
│   │     │          
│   │     └── images    <- contains all the hands images
│   │
│   ├── sf_36      <- Contains the script for the SF-36
│   │     │     
│   │     ├── README.md  <- contains all the information about the SF-36 and
│   │     │                 special selections. Including data structure.
│   │     ├── sf_36_english.txt  <- survey script
│   │     │     
│   │     └──sf_36_dutch.txt  <- surveys
│   ├── task_switch       <- Contains all the scripts and bitmaps for task switching
│   │     │     
│   │     ├── README.md  <- contains all the information about task_switching and
│   │     │                 special selections. Including data structure.
│   │     │     
│   │     ├── task_switch_experiment.txt  <- script for the experiment
│   │     │     
│   │     ├── task_switch_survey.txt  <- script for the survey to run task_switch
│   │     │          
│   │     └── task_switch_bitmaps    <- contains all the bitmaps used for task_switch
│   │
</pre>
