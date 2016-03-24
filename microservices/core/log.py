def set_logging():

    import logging
    import os

    logging.basicConfig(
        level=getattr(logging, os.environ.get('LOG_LEVEL', 'DEBUG')),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def get_logger(name=__name__):
    import logging
    return logging.getLogger(name)