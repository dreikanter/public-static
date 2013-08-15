# coding: utf-8

"""Custom exceptions."""


class BasicException(Exception):
    def __init__(self, **kwargs):
        self.params = kwargs

    def __str__(self):
        message = self.__doc__
        if hasattr(self, 'params'):
            params = map(lambda item: "%s=%s" % (item[0], item[1]), self.params.items())
            message = "%s: %s" % (message, ';'.join(params))
        return message


class NotImplementedException(BasicError):
    message = 'not implemented'
