import logging
from logstash_async.handler import AsynchronousLogstashHandler 
def setup_logger():
    log = logging.getLogger('shopshop_log')
    log.setLevel(logging.DEBUG)

    if not log.handlers:
        json_formatter = logging.Formatter('%(message)s')


        logstash_handler = AsynchronousLogstashHandler(
            host='logstash',
            port=8001,
            database_path=None,
            ssl_enable=False
        )
        logstash_handler.setFormatter(json_formatter)
        log.addHandler(logstash_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(json_formatter)
        log.addHandler(console_handler)
        
    return log

logger = setup_logger()