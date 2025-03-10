#!/usr/bin/env python3
import logging
import os
import inspect
from logging.handlers import RotatingFileHandler

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)

PATH = os.path.dirname(os.path.abspath(__file__))

log_formatter = logging.Formatter('%(asctime)s: %(name)s - %(levelname)s - %(message)s')

logFile = f'{current_dir}/SSID_CCG_log.log'

my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=50*1024*1024, 
                                 backupCount=5, encoding=None, delay=0)

my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)

logger = logging.getLogger('root')
logger.setLevel(logging.INFO)

logger.addHandler(my_handler)
