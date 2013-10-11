import sys
from publicstatic import conf
from publicstatic import cli
from publicstatic import logger
from publicstatic import source

from pprint import pprint

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


def dispatch(args):
    command = args.get('command')
    source = args.get('source', None)

    if command == 'init':
        publicstatic.init(source)
    elif command == 'build':
        publicstatic.build(source)
    elif command == 'run':
        port = args.get('port', None)
        browse = args.get('browse', False)
        publicstatic.run(source, port=port, browse=browse)
    elif command == 'deploy':
        publicstatic.deploy(source)
    elif command == 'clean':
        publicstatic.clean(source)
    elif command == 'page':
        name = args.get('name')
        force = args.get('force', False)
        edit = args.get('edit', False)
        publicstatic.page(source, name=name, force=force, edit=edit)
    elif command == 'post':
        name = args.get('name')
        force = args.get('force', False)
        edit = args.get('edit', False)
        publicstatic.post(source, name=name, force=force, edit=edit)
    elif command == 'update':
        publicstatic.update(source)
    elif command == 'image':
        subcommand = args.get('subcommand')
        if subcommand == 'add':
            pass
        elif subcommand == 'rm':
            pass
        elif subcommand == 'ls':
            pass


def main():
    try:
        dispatch(cli.parse(sys.argv[1:]))
    except USER_ERRORS as e:
        logger.error(e)
    except CRITICAL_ERRORS:
        logger.crash()
