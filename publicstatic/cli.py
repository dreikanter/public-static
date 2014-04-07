import argparse
from publicstatic import const
from publicstatic.version import __version__

# global arguments list (default value is a must for optionals!)
ARGS = {
    '--version': (
        ['-v', '--version'],
        {
            'action': 'version',
            'version': '%s v%s' % (const.GENERATOR, __version__),
            'help': 'print version number and exit',
        }
    ),
    '--dir': (
        ['-d', '--dir'],
        {
            'default': None,
            'metavar': 'DIR',
            'dest': 'path',
            'help': 'website source directory',
        }
    ),
    '--port': (
        ['-p', '--port'],
        {
            'default': None,
            'type': int,
            'dest': 'port',
            'help': 'port for local HTTP server',
        }
    ),
    '--browse': (
        ['-b', '--browse'],
        {
            'action': 'store_true',
            'default': False,
            'dest': 'browse',
            'help': 'open in default browser',
        }
    ),
    '--force': (
        ['-f', '--force'],
        {
            'action': 'store_true',
            'default': False,
            'dest': 'force',
            'help': 'overwrite existing file',
        }
    ),
    '--edit': (
        ['-e', '--edit'],
        {
            'action': 'store_true',
            'default': False,
            'dest': 'edit',
            'help': 'open with text editor',
        }
    ),
    '--def-tpl': (
        ['-t', '--def-tpl'],
        {
            'action': 'store_true',
            'default': False,
            'dest': 'def_tpl',
            'help': 'use default templates',
        }
    ),
    'path': (
        ['path'],
        {
            'nargs': '?',
            'default': None,
            'help': 'path to the new site directory (default is cwd)',
        },
    ),
    'name': (
        ['name'],
        {
            'help': 'new entry title'
        },
    ),
    'filename': (
        ['filename'],
        {
            'help': 'image file name',
        },
    ),
    'id?': (
        ['id'],
        {
            'nargs': '?',
            'default': None,
            'help': 'image identifier',
        },
    ),
    'id': (
        ['id'],
        {
            'default': None,
            'help': 'image identifier',
        },
    ),
    'number': (
        ['number'],
        {
            'default': const.LS_NUM,
            'nargs': '?',
            'type': int,
            'metavar': 'N',
            'help': 'output last N lines (default is %d)' % const.LS_NUM,
        },
    ),
}

# parser configuration
CONF = {
    'args': ['--version'],
    'subparsers': [
        {
            'name': 'init',
            'args': ['path', '--force'],
            'help': 'initialize new website',
        },
        {
            'name': 'build',
            'args': ['--dir', '--def-tpl'],
            'help': 'generate web content from source',
        },
        {
            'name': 'run',
            'args': ['--dir', '--port', '--browse'],
            'help': 'run local web server to preview generated website',
        },
        {
            'name': 'deploy',
            'args': ['--dir'],
            'help': 'deploy generated website to the remote web server',
        },
        {
            'name': 'clean',
            'args': ['--dir'],
            'help': 'delete all generated content',
        },
        {
            'name': 'page',
            'args': ['name', '--dir', '--force', '--edit'],
            'help': 'create new page',
        },
        {
            'name': 'post',
            'args': ['name', '--dir', '--force', '--edit'],
            'help': 'create new post',
        },
        # {
        #     'name': 'image',
        #     'args': [],
        #     'help': 'image management commands group',
        #     'subparsers': [
        #         {
        #             'name': 'add',
        #             'args': ['filename', 'id?', '--dir'],
        #             'help': 'add new image with optional id'
        #         },
        #         {
        #             'name': 'rm',
        #             'args': ['id', '--dir'],
        #             'help': 'remove image'
        #         },
        #         {
        #             'name': 'ls',
        #             'args': ['number', '--dir'],
        #             'help': 'list images'
        #         },
        #     ],
        # },
    ],
}

# common subparser configuration
SUBPARSER_CONF = {
    'metavar': '<command>',
    'dest': 'command',
    'help': '',
}


def configure_parser(parser, conf, arguments):
    for arg_name in conf.get('args', []):
        args, kwargs = arguments[arg_name]
        parser.add_argument(*args, **kwargs)

    if 'subparsers' in conf:
        subparsers = parser.add_subparsers(**SUBPARSER_CONF)
        for sp in conf['subparsers']:
            subparser = subparsers.add_parser(sp['name'], help=sp['help'])
            configure_parser(subparser, sp, arguments)


def parse(args):
    epilog = ("See '%s <command> --help' for more details "
              "on a specific command usage.") % const.PROG
    parser = argparse.ArgumentParser(prog=const.PROG, epilog=epilog)
    configure_parser(parser, CONF, ARGS)
    if not args:
        parser.print_help()
    return vars(parser.parse_args(args))
