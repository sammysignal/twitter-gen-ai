import logging
#logging.basicConfig(filename='pierre.log', encoding='utf-8', level=logging.DEBUG)

def getPierreLogger():
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler = logging.FileHandler('pierre.log')
    handler.setFormatter(formatter)
    logger = logging.getLogger('pierre')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger

p_logger = getPierreLogger()
