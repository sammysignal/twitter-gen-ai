import logging

# logging.basicConfig(filename='pierre.log', encoding='utf-8', level=logging.DEBUG)


# Custom logger which wraps logging.logger
class PierreLogger:
    def __init__(self):
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler = logging.FileHandler("pierre.log")
        handler.setFormatter(formatter)
        logger = logging.getLogger("pierre")
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        # Set class variables
        self.logger = logger
        self.logBuffer = ""

    def info(self, s):
        self.logBuffer = self.logBuffer + "INFO: " + str(s) + "\n"
        self.logger.info(s)

    def error(self, s):
        self.logBuffer = self.logBuffer + "ERROR: " + str(s) + "\n"
        self.logger.error(s)

    def getLogBuffer(self):
        return self.logBuffer


p_logger = PierreLogger()
