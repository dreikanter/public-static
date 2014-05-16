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
    '--source': (
        ['-s', '--source'],
        {
            'default': '.',
            'metavar': 'DIR',
            'dest': 'source',
            'help': 'website source directory path',
        }
    ),
    '--output': (
        ['-o', '--output'],
        {
            'default': None,
            'metavar': 'DIR',
            'dest': 'output',
            'help': 'build output path',
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
    '--safe': (
        ['-a', '--safe'],
        {
            'action': 'store_true',
            'default': False,
            'dest': 'safe',
            'help': 'backup previous version',
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
            'args': ['--source', '--output'],
            'help': 'generate web content from source',
        },
        {
            'name': 'run',
            'args': ['--source', '--port', '--browse'],
            'help': 'run local web server to preview generated website',
        },
        {
            'name': 'deploy',
            'args': ['--source'],
            'help': 'deploy generated website to the remote web server',
        },
        {
            'name': 'clean',
            'args': ['--source'],
            'help': 'delete all generated content',
        },
        {
            'name': 'page',
            'args': ['name', '--source', '--force', '--edit'],
            'help': 'create new page',
        },
        {
            'name': 'post',
            'args': ['name', '--source', '--force', '--edit'],
            'help': 'create new post',
        },
        {
            'name': 'theme',
            'args': [],
            'help': 'theme maintenance operations',
            'subparsers': [
                {
                    'name': 'update',
                    'args': ['--source', '--safe'],
                    'help': 'update theme template and assets',
                },
            ],
        },
    ],
}


def configure_parser(parser, conf, arguments, depth=0):
    for arg_name in conf.get('args', []):
        args, kwargs = arguments[arg_name]
        parser.add_argument(*args, **kwargs)

    if 'subparsers' in conf:
        subparsers = parser.add_subparsers(**{
            'metavar': '<command>',
            'dest': "command%s" % ('' if depth < 1 else str(depth+1)),
            'help': '',
        })
        for sp in conf['subparsers']:
            subparser = subparsers.add_parser(sp['name'], help=sp['help'])
            configure_parser(subparser, sp, arguments, depth+1)


def parse(args):
    epilog = ("See '%s <command> --help' for more details "
              "on a specific command usage.") % const.PROG
    parser = argparse.ArgumentParser(prog=const.PROG, epilog=epilog)

    configure_parser(parser, CONF, ARGS)
    if not args:
        parser.print_help()
    return vars(parser.parse_args(args))
