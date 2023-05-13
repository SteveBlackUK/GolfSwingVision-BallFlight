import logging
from logtail import LogtailHandler

handler = LogtailHandler(source_token="pYmqvWZAZqJdyH3dcVWcNMMG")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.handlers = []
logger.addHandler(handler)
