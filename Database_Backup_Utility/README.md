**Database Backup Utility**


This database backup utility is a CLI tool which allows users to backup, restore, and delete created backups for various Database types. Tables / Collections can also be individually backed up as .csv files, and can be viewed within the tool. The database connection can be tested to ensure that it is working and available to use, and backups can also optionally be compressed with a chosen amount from 1-10. Currently, this tool only supports postgresql, sqlite, and mongodb, but may be updated in the future to support more database types. Backups can optionally be stored in the cloud using an s3 bucket (only option at the moment), or else stored locally.
This was built with Typer for the CLI commands, and utilises various database specific tools/libraries such as pg_dump and pymongo for database management.   
Tests were written in pytest with prompting given to claude, and currently 3/4 of the tests are working.





#### **To run and test on Windows:** 

1) Clone the repo with svn:  
` svn export https://github.com/asiratongue/intermediate-backend-projects/tree/main/RealTimeLeaderboard`

2) Create and activate the virtual environment from terminal with:  
   `python3 -m venv venv`  
   `PS venv\Scripts\activate (on Windows)`
   
3) Install the dependencies from terminal with:  
   `pip install -r requirements.txt`
   
4) configure chosen database settings if using for example:  

   `config path: \Database_Backup_Utility\src\config\config_postgresql.json`
       
   `{`  
`"host":"YOUR_HOST_NAME",`  
`"port":"YOUR_PORT",`  
`"database":"YOUR_DATABASE_NAME",`  
`"user":"YOUR_USERNAME",`  
`"password":"YOUR_PASSWORD",`  
`"Local" : LOCAL_OR_CLOUD?(TRUE/FALSE),`  
`"type" : "postgresql"`  
`}) `  


5) Configure cloud storage settings if using like so:    
`config_path: \Database_Backup_Utility\src\config\s3_config.json`   
`{`  
    `"BucketName": "YOUR_BUCKET_NAME",`  
    `"Region": "YOUR_REGION",`  
    `"AccessControl": "Private",`  
    `"Versioning": false,`  
    `"Encryption": true`  
  `}`    
   
6) Use the app!   
`python main.py backup postgresql G:\01101000111101\Programming\Projects\intermediate-backend-projects\Database_Backup_Utility -c 2`


## Commands

### **test-connection:**   
Test the connection of your configured database, returns the status response of the chosen db. 

  
#### **arguments:**   
**db_type** - the type of database that one is testing (Mongodb, postgresql, sqlite).  
                                                                                                                                                 
### **view:**              
View all the tables/collections within your configured database.

#### **arguments:**   
**db_type** - the type of database that one is viewing (Mongodb, postgresql, sqlite).  

### **backup:**              
Backup your configured database to selected location, choose between a full sql dump or individual csv tables.  

#### **arguments:**   
**db_type** - the type of database to back up (postgresql, sqlite, mongodb.  
**backup_path** - full path to where the backup will be saved.  
**storage** - optionally select "cloud" within your command, backs up to the cloud, will save locally first.  
**compression**, "--compression", "-c" - choose data compression level, values from 1-9. default value is 10 (no compression)


### **delete-backup:**  
Delete any listed backups.  

### **restore:**  
restore configured database from full sql dump or selected csv table.  

#### **arguments:**   
**db_type** - type of database to back up (postgresql, sqlite, mongodb.  


## **TODO:**

add some form of mongodb validation,  
slack notifications,    
support for more databases + cloud storage solutions,    
implement differential and incremental backup,    
Optimize backup operations for large databases utilizing chunking or other methods,     
refactor and ensure all tests are working properly.
 
