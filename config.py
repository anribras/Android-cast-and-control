import logging
import logging.config
import sys, os

def log_init(path=None, item=None):
    logging.config.fileConfig(path)
    return logging.getLogger(item)

def static_vars(**kwargs):
    """
    static vars decorater
    """
    #funciton static variable as C
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate



LOGGER=log_init(r'logger.conf','pylink')


