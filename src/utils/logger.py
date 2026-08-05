import logging, sys
def get_logger():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)
    return logging.getLogger(__name__)
logger = get_logger()