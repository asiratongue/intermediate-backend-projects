import psycopg2
import logging
from datetime import datetime
import typer
import pymongo
import sqlite3
from src.config import config_manager

configs = config_manager.load_configs()
app = typer.Typer()
logger = logging.getLogger('DBMS_log')


def formatted_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]

"""DB CONNECTION FUNCTION - RETURNS A CONNECTION"""
def connect_db(db_data):
    try:
        logger.info(f'attempting connection, @ {formatted_timestamp()}')
        if db_data["type"].lower() == "postgresql":
                conn = psycopg2.connect(
                host=db_data["host"],
                port=db_data["port"],
                database=db_data["database"],
                user=db_data["user"],
                password=db_data["password"],
                sslmode="prefer"
            )
                print(f"Connected successfully to PostgreSQL database @ {formatted_timestamp()}")
                return conn

        if db_data["type"].lower() == "sqlite": 
                         
                conn = sqlite3.connect(db_data["path"])
                print(f"Connected successfully to sqlite3 database @ {formatted_timestamp()}")
                return conn

        elif db_data["type"].lower() == "mongodb":
            mongo_client = pymongo.MongoClient(db_data["connection_string"] + "/?retryWrites=true&w=majority") 
            db = mongo_client[db_data["database"]]
            mongo_client.admin.command('ping')
            print(f"Connected successfully to MongoDB Atlas @ {formatted_timestamp()}")
            return mongo_client, db 
            
        else:
            logger.error(f"Unsupported database type: {db_data['type']}")
            return None
            
    except Exception as e:
        logger.error(f"Error: Unable to connect to database. Details : {e}") 
        return None