def set_logging(level='DEBUG', log_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'):

    import logging
    import os

    logging.basicConfig(
        level=getattr(logging, os.environ.get('LOG_LEVEL', level)),
        format=log_format,
    )

def get_logger(name=__name__):
    import logging
    return logging.getLogger(name)