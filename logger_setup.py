import logging

def configure_logger():
    # Create a logger
    logger = logging.getLogger('logs')
    logger.setLevel(logging.DEBUG)

    # Configure the logging format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Create a file handler for all levels
    file_handler = logging.FileHandler('server.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger (no console handler)
    logger.addHandler(file_handler)

    return logger
