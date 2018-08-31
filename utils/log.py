import logging
from logging.handlers import WatchedFileHandler

from config import SERVER_LOG_PATH, LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL,
                    format='%(levelname)s %(asctime)s %(module)s %(message)s',
                    handlers=[WatchedFileHandler(SERVER_LOG_PATH, "w")])
server_logger = logging.getLogger('picture_server')