import logging
import sys


def setup_logger():
    # implement file handler if needed
    stdout_handler = logging.StreamHandler(sys.stdout)
    handlers = [stdout_handler]

    logging.basicConfig(
        level=logging.DEBUG,
        format=(
            '[%(asctime)s] {%(filename)s:%(lineno)d}'
            ' %(levelname)s - %(message)s'
        ),
        handlers=handlers
    )
