# coding: utf-8

import argparse


class CustomFormatter(argparse.HelpFormatter):

    def _metavar_formatter(self, action, default_metavar):
        if action.metavar is not None:
            result = action.metavar
        elif action.choices is not None:
            result = ''
        else:
            result = default_metavar

        def format(tuple_size):
            if isinstance(result, tuple):
                return result
            else:
                return (result, ) * tuple_size
        return format
