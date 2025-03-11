import logging
from pathlib import Path

def setup_logger():

    logger = logging.getLogger('DBMS_log')
    logger.setLevel(logging.DEBUG)
    

    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        log_path = Path(__file__).parent / 'logs' / 'DBMS_log.log'
        log_path.parent.mkdir(exist_ok=True) 
        fh = logging.FileHandler(log_path)
        fh.setLevel(logging.ERROR)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
        
        logger.addHandler(ch)
        logger.addHandler(fh)
    
    return logger

# Create a global logger instance
logger = setup_logger()

