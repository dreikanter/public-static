# coding: utf-8

"""Custom exceptions."""


class BasicError(Exception):
    def __str__(self):
        return self.message


class NotImplementedException(BasicError):
    message = 'not implemented'
