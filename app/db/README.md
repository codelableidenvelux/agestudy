# Db2
This folder contains the files to talk to the database, create tables, delete table and insert test data into the database.

## Get started
The library to talk to db2 is ibm_db

### Install
```
$ pip3 install ibm_db
```

Read [this](https://www.ibm.com/support/knowledgecenter/SSEPGG_11.5.0/com.ibm.swg.im.dbclient.python.doc/doc/t0054367.html) for detailed information on ibm_db download and setup

# Folder Overview
<pre>
│              
├── db        
│   │
│   ├── README.md
│   │         
│   ├── python_2_db2.py    <- class Db connects to db and executes sql queries
│   │                
│   ├── tables.sql         <- Creates the tables used for agestudy
│   │    
│   ├── test.sql           <- Inserts test data in sql table
│   │    
│   ├── delete.sql         <- Delete the sql tables
</pre>

# Database tables information
## Session_info
The table session_info contains the user information. They provide it at register.

| Session_info      | Type                         | Explanation
|-------------------|------------------------------|---------------------------------------------------|
| user_id           | INT NOT NULL PRIMARY KEY     | number to describe user                           |
| user_name         | VARCHAR(255) NOT NULL UNIQUE | user name                                         |
| email             | VARCHAR(1000) NOT NULL       | email                                             |
| gender            | INT NOT NULL                 | gender, 1 male, 2 female 3 other                  |
| collect_possible  | INT NOT NULL                 | if user can collect the money 1 else 0            |
| for_money         | INT NOT NULL                 | if user wants to participate for money 1 else 0   |
| user_type         | INT NOT NULL                 | If both collect_possible and for_money is 1 then 1|
|                   |                              | else 0 because user cant participate for money    |
| birthyear         | DATE NOT NULL                | Month and year of birth                           |
| pas_hash          | VARCHAR(255) NOT NULL        | Password hash                                     |

## Tasks
Contains information about the tasks, id, name, psytoolkit link etc.

| Tasks     | Type                      | Explanation                           |
|-----------|---------------------------|---------------------------------------|
| task_id   | INT NOT NULL PRIMARY KEY  | A number to describe each task        |
| task_link | VARCHAR(255)              | Psytoolkit link to the task           |
| task_name | VARCHAR (100) NOT NULL    | Name of the task                      |
| frequency | DECIMAL(3,2) NOT NULL     | How often the task can be completed   |
| price     | DECIMAL(5,3) NOT NULL     | the amount user can earn for the task |

## Task_completed
Keeps track of the completed tasks.

| Task_completed | Type                                | Explanation                                                            |
|----------------|-------------------------------------|------------------------------------------------------------------------|
| time_exec      | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | Time task was completed                                                 |
| user_id        | INT NOT NULL FOREIGN KEY            | user_id from session_info table                                        |
| task_id        | INT NOT NULL FOREIGN KEY            | task_id from tasks table                                               |
| collect        | INT NOT NULL                        | Status of money collection,  if the money was collected then 0 else 1  |

## Tracked_task
Keeps track of the opening and closing of the tasks.

| Tracked_task | Type                                | Explanation                            |
|--------------|-------------------------------------|----------------------------------------|
| time_exec    | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | Time task was executed                 |
| user_id      | INT NOT NULL FOREIGN KEY            | user_id from session_info table        |
| task_id      | INT NOT NULL FOREIGN KEY            | task_id from tasks table               |
| status       | INT NOT NULL                        | status of task, 1 for completed else 0 |
