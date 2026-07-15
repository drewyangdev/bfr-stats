import os
import sys
import io
import logging
import logging.handlers

# get logger level
DEBUG = os.getenv("DEBUG", "True") == "True"
# set logger config
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
    handlers=[
        ## log in console
        logging.StreamHandler(sys.stdout),
        # ## log in rotating file
        # ## only file log: python app.py > /dev/null 2>&1 &
        # logging.handlers.RotatingFileHandler(
        #     "debug.log", maxBytes=1024 * 1024 * 10, backupCount=5, encoding="utf-8"
        # ),
    ],
)

# set logger level
logger = logging.getLogger(__name__)
if DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)