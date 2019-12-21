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
