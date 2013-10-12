import sys
from publicstatic import conf
from publicstatic import cli
from publicstatic import logger
from publicstatic import publicstatic
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


def dispatch(args):
    command = args.get('command')
    directory = args.get('directory', None)

    if command == 'init':
        publicstatic.init(directory)
    elif command == 'build':
        publicstatic.build(directory)
    elif command == 'run':
        port = args.get('port', None)
        browse = args.get('browse', False)
        publicstatic.run(directory, port=port, browse=browse)
    elif command == 'deploy':
        publicstatic.deploy(directory)
    elif command == 'clean':
        publicstatic.clean(directory)
    elif command == 'page':
        name = args.get('name')
        force = args.get('force', False)
        edit = args.get('edit', False)
        publicstatic.page(directory, name=name, force=force, edit=edit)
    elif command == 'post':
        name = args.get('name')
        force = args.get('force', False)
        edit = args.get('edit', False)
        publicstatic.post(directory, name=name, force=force, edit=edit)
    elif command == 'update':
        publicstatic.update(directory)
    elif command == 'image':
        subcommand = args.get('subcommand')
        if subcommand == 'add':
            file_name = args.get('filename')
            image_id = args.get('id', None)
            publicstatic.image_add(directory, file_name, image_id)
        elif subcommand == 'rm':
            image_id = args.get('id', None)
            publicstatic.image_rm(directory, image_id)
        elif subcommand == 'ls':
            number = args.get('number', None)
            publicstatic.image_ls(directory, number)


def main():
    try:
        dispatch(cli.parse(sys.argv[1:]))
    except USER_ERRORS as e:
        logger.error(e)
    except CRITICAL_ERRORS:
        logger.crash()
