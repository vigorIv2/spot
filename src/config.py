#!/usr/bin/python
"""
basic config and factory setup for application
"""
import logging
from logging import handlers
from yaml import load


def init_logger():
    """Example function with types documented in the docstring.
    Args:
    Returns:
    """
    lformat = "%(asctime)s [%(levelname)-5.5s] [%(name)s] [%(threadName)-12.12s]  %(message)s"

    logging.basicConfig(
        level=logging.INFO,
        format=lformat,
        )

    file_handler = handlers.RotatingFileHandler(
        "{0}/{1}.log".format('.', 'meta-meta-hive'),
        maxBytes=(50*1024*1024),
        backupCount=7
        )
    file_handler.setFormatter(logging.Formatter(lformat))
    logging.getLogger().addHandler(file_handler)
    return


def init_config(env):
    """ Initialize config, load fomr corresponding file depending on paramater
    """
    doc = ''
    if env == 'local':
        with open('./config/local.yml', 'r') as f:
            doc = load(f)
    elif env == 'staging':
        with open('./config/staging.yml', 'r') as f:
            doc = load(f)
    elif env == 'prod':
        with open('./config/prod.yml', 'r') as f:
            doc = load(f)
    else:
        with open(env, 'r') as f:
            doc = load(f)
    if doc == '':
        logging.error("Couldn't load config properly")
    return doc
