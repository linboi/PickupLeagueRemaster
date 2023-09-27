import logging

class Logger:
    def __init__(self) -> None:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        f_handler = logging.FileHandler('file.log', encoding='utf-8')
        f_format = logging.Formatter('[%(asctime)s] [%(levelname)s] : %(message)s', datefmt='%Y-%m-%d %H:%M:%S', )
        f_handler.setFormatter(f_format)
        logger.addHandler(f_handler)
        self.logger = logger


