# coding: utf-8

"""Custom exceptions."""


class BasicException(Exception):
    def __init__(self, **kwargs):
        self.params = kwargs

    def __str__(self):
        message = self.__doc__
        if hasattr(self, 'params') and self.params:
            params = ["%s=%s" % (p[0], p[1]) for p in self.params.items()]
            message = "%s: %s" % (message, ';'.join(params))
        return message


class NotImplementedException(BasicException):
    message = 'not implemented'
