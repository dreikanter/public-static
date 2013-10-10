import sys
from publicstatic import conf
from publicstatic import cli
from publicstatic import logger
from publicstatic import source

USER_ERRORS = (
    conf.NotFoundException,
    conf.DirectoryExistsException,
    source.PageExistsException
)

CRITICAL_ERRORS = (
    conf.ParsingError,
    conf.NotInitializedException,
    source.NotImplementedException,
    Exception
)


def main():
    try:
        print(cli.parse(sys.argv[1:]))
    except USER_ERRORS as e:
        logger.error(e)
    except CRITICAL_ERRORS:
        logger.crash()
