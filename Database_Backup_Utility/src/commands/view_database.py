from utils.logger_setup import logger
from config import config_manager
from src.commands.connection_test import connection_test
from utils.connect_db import connect_db

configs = config_manager.load_configs()

"""VIEW DATABASE TABLES FUNCTION"""
def view(db: str):

    if db == "sqlite":
        conn = connect_db(configs["sqlite"])
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        logger.info(f"Connected to sqlite database:,  location: {conn.execute("PRAGMA database_list").fetchone()[2]}")
    
    if db == "postgresql":
        conn = connect_db(configs["postgresql"])       
        cur = conn.cursor()
        cur.execute("SELECT relname FROM pg_class WHERE relkind='r' AND relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')")
        logger.info(f"Connected to database: {conn.info.dbname} as user: {conn.info.user}")

    if db == "mongodb":
        client, db = connect_db(configs["mongodb"])
        collections = db.list_collection_names()

        for collection in collections:
            print("collection name: ", collection)
        return
    
    elif db not in ["sqlite", "postgresql", "mongodb"]:
        logger.error("you must enter a valid database type! -> (postgres, sqlite, mongodb)")
        return 
    #Continuation of SQL logic
    tables = cur.fetchall()

    if not tables:
        logger.error("no tables found in schema!")
        return
        
    for table in tables:
        print("table name: ", table[0])        
        conn.close()
    return