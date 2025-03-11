import os
import json
from pathlib import Path
import boto3
from boto3.session import Config
import logging

logger = logging.getLogger('DBMS_log')
backup_list_path = Path(r"G:\01101000111101\Programming\Projects\intermediate-backend-projects\Database_Backup_Utility\src\config")

def load_configs():

    original_dir = os.getcwd()

    try:

        postgresql_config = {}
        mongodb_config = {}
        s3_config = {}

        try:
            with open(Path(backup_list_path,'config_postgresql.json'), 'r') as file:
                file.seek(0, 2)  
                if file.tell() > 0:  
                    file.seek(0)  
                    postgresql_config = json.load(file)
        except(FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Warning: Could not load PostgreSQL config: {e}")
            
        try:
            with open(Path(backup_list_path, 'config_mongodb.json'), 'r') as file:
                file.seek(0, 2)  
                if file.tell() > 0:  
                    file.seek(0)  
                    mongodb_config = json.load(file)
                if mongodb_config:
                    mongo_connection_string = mongodb_config["protocol"] + mongodb_config["user"] + mongodb_config["password"] + mongodb_config["host"]
                    mongodb_config["connection_string"] = mongo_connection_string

        except(FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Warning: Could not load MongoDB config: {e}")

        s3 = None
        s3_client = None
        bucket = None

        try:
            with open(Path(backup_list_path, 's3_config.json'), 'r') as file:
                file.seek(0, 2)  
                if file.tell() > 0:  
                    file.seek(0)  
                    s3_config = json.load(file)

                if s3_config:

                    aws_config = Config(region_name = s3_config["Region"], 
                                        signature_version = 'v4',
                                        retries = {'max_attempts': 10, 'mode': 'standard'
                                    })

                    s3 = boto3.resource('s3', config=aws_config)
                    s3_client = boto3.client('s3')
                    bucket = s3.Bucket(s3_config["BucketName"])

                    s3_config["s3"] = s3
                    s3_config["s3_client"] = s3_client
                    s3_config["bucket"] = bucket

        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            logger.error(f"Warning: Could not load S3 config: {e}")


        ''' SQLITE CONFIG (CHANGE PATH + DB NAME) '''
        sqlite_config = {"type" : "sqlite", "path" : Path("G:/01101000111101/Programming/Projects/intermediate-backend-projects/E_Commerce_API/db.sqlite3"), "database" : "ecom_basic_database"}

        config_dict = {"postgresql": postgresql_config, "sqlite" : sqlite_config, "mongodb" : mongodb_config, "s3" : s3_config}

        return config_dict
    
    finally:
        os.chdir(original_dir)