#
# Copyright (c) 2023 CUJO LLC
#
"""
Main package for CUJO SRL BIP.
"""
import os
import logging.config
from functools import partialmethod, partial

import yaml
from dotenv import load_dotenv

# Package constants
__program__ = "bip"
__version__ = "0.1.0-no_git"
__description__ = ""

# Load .env
load_dotenv(os.getcwd() + "/.env")

####################################################################################################
# Setup logging

# Add custom log levels, pythonic way: https://stackoverflow.com/a/55276759
logging.TRACE = 5
logging.addLevelName(logging.TRACE, "TRACE")
logging.Logger.trace = partialmethod(logging.Logger.log, logging.TRACE)
logging.trace = partial(logging.log, logging.TRACE)

# Configure logging
logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG").upper())
with open("logging.yaml", "rt", encoding="utf8") as fp:
    log_config = yaml.safe_load(fp.read())
    logging.config.dictConfig(log_config)

# Silence talky loggers
logging.getLogger("urllib3").setLevel("WARNING")
logging.getLogger("filelock").setLevel("WARNING")

# Log version
logging.getLogger("bip").info("BIP %s", __version__)
