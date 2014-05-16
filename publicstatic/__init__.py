import sys
from publicstatic import conf
from publicstatic import cli
from publicstatic import logger
from publicstatic import publicstatic
from publicstatic import source

USER_ERRORS = (
    conf.NotFoundException,
    conf.ConfigurationExistsException,
    source.PageExistsException,
)

CRITICAL_ERRORS = (
    conf.ParsingError,
    conf.NotInitializedException,
    source.NotImplementedException,
    Exception,
)


def dispatch(args):
    command = args.get('command')
    source = args.get('source')
    if command == 'init':
        publicstatic.init(source, args['force'])
    elif command == 'build':
        publicstatic.build(source, args['output'])
    elif command == 'run':
        publicstatic.run(source, args['port'], args['browse'])
    elif command == 'deploy':
        publicstatic.deploy(source)
    elif command == 'clean':
        publicstatic.clean(source)
    elif command == 'page':
        publicstatic.page(source, args['name'], args['force'], args['edit'])
    elif command == 'post':
        publicstatic.post(source, args['name'], args['force'], args['edit'])
    elif command == 'theme':
        subcommand = args.get('command2')
        if subcommand == 'update':
            publicstatic.theme_update(source, args['safe'])


def main():
    try:
        dispatch(cli.parse(sys.argv[1:]))
    except USER_ERRORS as e:
        logger.error(e)
    except CRITICAL_ERRORS:
        logger.crash()
