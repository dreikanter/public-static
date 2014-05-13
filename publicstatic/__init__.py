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
    path = args.get('path', '.')
    if command == 'init':
        publicstatic.init(path, args['force'])
    elif command == 'build':
        publicstatic.build(path)
    elif command == 'run':
        publicstatic.run(path, args['port'], args['browse'])
    elif command == 'deploy':
        publicstatic.deploy(path)
    elif command == 'clean':
        publicstatic.clean(path)
    elif command == 'page':
        publicstatic.page(path, args['name'], args['force'], args['edit'])
    elif command == 'post':
        publicstatic.post(path, args['name'], args['force'], args['edit'])
    # elif command == 'image':
    #     subcommand = args.get('subcommand')
    #     if subcommand == 'add':
    #         publicstatic.image_add(path, args['filename'], args['id'])
    #     elif subcommand == 'rm':
    #         publicstatic.image_rm(path, args['id'])
    #     elif subcommand == 'ls':
    #         publicstatic.image_ls(path, args['number'])


def main():
    try:
        dispatch(cli.parse(sys.argv[1:]))
    except USER_ERRORS as e:
        logger.error(e)
    except CRITICAL_ERRORS:
        logger.crash()
