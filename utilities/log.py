import logging
import inspect

class Logger:
    @staticmethod
    def get_logger(name=None):
        if name is None:
            # Automatically get the name of the calling class or module
            frame = inspect.currentframe().f_back
            name = frame.f_globals["__name__"]
            if "self" in frame.f_locals:
                name = frame.f_locals["self"].__class__.__name__

        logger = logging.getLogger(name)
        if not logger.hasHandlers():
            # Set the logging level
            logger.setLevel(logging.DEBUG)

            # Create a console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)

            # Create a formatter and set it for the handler
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)

            # Add the handler to the logger
            logger.addHandler(console_handler)

        return logger