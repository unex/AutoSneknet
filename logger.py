import sys
import __main__
import logging
import traceback

from logging.handlers import RotatingFileHandler

formatter = logging.Formatter(f'[%(asctime)s][%(levelname)s] %(message)s')

log = logging.getLogger('AutoSneknet')
log.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setFormatter(formatter)
console.setLevel(logging.CRITICAL)
log.addHandler(console)

file = RotatingFileHandler(__main__.__file__ + '.log', mode='a', maxBytes=1024, backupCount=0, encoding=None, delay=0)
file.setFormatter(formatter)
file.setLevel(logging.DEBUG)
log.addHandler(file)

def except_handler(type_, value, tb):
    if type_ is KeyboardInterrupt:
        return

    t = ''.join(traceback.format_tb(tb))
    log.critical(f'FATAL ERROR: {type_.__name__}\n\n{t}\n{value}')

sys.excepthook = except_handler
