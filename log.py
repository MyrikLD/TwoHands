import logging
import sys
from logging.handlers import RotatingFileHandler


def Log(name):
	# logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s', datefmt='%H:%M:%S')

	handler = RotatingFileHandler('log.log', maxBytes=100000, backupCount=1)
	handler.setLevel(logging.INFO)
	formatter = logging.Formatter('%(asctime)s.%(msecs)03d [%(name)s] %(levelname)s %(message)s',
	                              datefmt='%Y-%m-%d %H:%M:%S')
	handler.setFormatter(formatter)
	# handler.addFilter(NoCamFilter())

	handler_err = logging.StreamHandler(sys.stdout)
	formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s %(message)s', datefmt='%H:%M:%S')
	handler_err.setFormatter(formatter)
	handler_err.setLevel(logging.DEBUG)

	logger = logging.getLogger(str(name))

	logger.setLevel(logging.DEBUG)
	logger.addHandler(handler)
	logger.addHandler(handler_err)

	return logger
