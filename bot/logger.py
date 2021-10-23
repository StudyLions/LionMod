import sys
import logging

from cmdClient.logger import cmd_log_handler


# Setup the logger
logger = logging.getLogger()
log_fmt = logging.Formatter(fmt='[{asctime}][{levelname:^8}] {message}', datefmt='%d/%m | %H:%M:%S', style='{')
term_handler = logging.StreamHandler(sys.stdout)
term_handler.setFormatter(log_fmt)
logger.addHandler(term_handler)
logger.setLevel(logging.INFO)


# Define the context log format and attach it to the command logger as well
@cmd_log_handler
def log(message, context="GLOBAL", level=logging.INFO, post=True):
    # Add prefixes to lines for better parsing capability
    lines = message.splitlines()
    if len(lines) > 1:
        lines = [
            '┌ ' * (i == 0) + '│ ' * (0 < i < len(lines) - 1) + '└ ' * (i == len(lines) - 1) + line
            for i, line in enumerate(lines)
        ]
    else:
        lines = ['─ ' + message]

    for line in lines:
        logger.log(level, '\b[{}] {}'.format(
            str(context).center(22, '='),
            line
        ))
