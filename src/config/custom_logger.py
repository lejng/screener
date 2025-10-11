import logging


class CustomLogger:

    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s: - %(asctime)s - %(filename)s:%(lineno)d - %(message)s',
            handlers=[
                #logging.FileHandler('logs/app.log'),
                # this is console log
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def log_info(self, message: str):
        self.logger.info(message, stacklevel=2)

    def log_error(self, message: str):
        self.logger.error(message, stacklevel=2)