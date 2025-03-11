from utils.logger_setup import logger
from config import config_manager
from utils.connect_db import connect_db

configs = config_manager.load_configs()


"""TEST CONNECTION FUNCTION"""

def connection_test(db_type : str):
    logger.info(f"configs: {configs}")
    if db_type == "postgresql":
        x = connect_db(configs["postgresql"])      
    elif db_type == "sqlite":
        x = connect_db(configs["sqlite"])
    elif db_type == "mongodb":
        x = connect_db(configs["mongodb"])
    else:
        print(f"Unknown database type: {db_type}")
        return
    
    print(f"connection to {configs[db_type]["database"]} is ok!")