import logging


logging.basicConfig(filename='Job_logs.log', filemode='a', format='%(asctime)s - %(message)s',
                    datefmt="%m/%d/%Y %H:%M:%S %Z", level=logging.INFO)