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
    src_dir = args.get('src_dir', None)

    if command == 'init':
        publicstatic.init(src_dir)
    elif command == 'build':
        def_tpl = args.get('def_tpl', False)
        publicstatic.build(src_dir, def_tpl=def_tpl)
    elif command == 'run':
        port = args.get('port', None)
        browse = args.get('browse', False)
        publicstatic.run(src_dir, port=port, browse=browse)
    elif command == 'deploy':
        publicstatic.deploy(src_dir)
    elif command == 'clean':
        publicstatic.clean(src_dir)
    elif command == 'page':
        name = args.get('name')
        force = args.get('force', False)
        edit = args.get('edit', False)
        publicstatic.page(src_dir, name=name, force=force, edit=edit)
    elif command == 'post':
        name = args.get('name')
        force = args.get('force', False)
        edit = args.get('edit', False)
        publicstatic.post(src_dir, name=name, force=force, edit=edit)
    elif command == 'image':
        subcommand = args.get('subcommand')
        if subcommand == 'add':
            file_name = args.get('filename')
            image_id = args.get('id', None)
            publicstatic.image_add(src_dir, file_name, image_id)
        elif subcommand == 'rm':
            image_id = args.get('id', None)
            publicstatic.image_rm(src_dir, image_id)
        elif subcommand == 'ls':
            number = args.get('number', None)
            publicstatic.image_ls(src_dir, number)


def main():
    try:
        dispatch(cli.parse(sys.argv[1:]))
    except USER_ERRORS as e:
        logger.error(e)
    except CRITICAL_ERRORS:
        logger.crash()
