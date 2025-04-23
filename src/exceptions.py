"""
This file contains all exceptions raised by the application.
"""


class InvalidConfigurationException(Exception):
    """
    Exception raised when there is a misconfiguration.
    """

class VocabularyLoadingException(Exception):
    """
    Exception raised when there is a problem loading the vocabulary.
    """


class UnknownAuthenticationTypeException(InvalidConfigurationException):
    """
    Exception raised when the authentication type specified is not known.
    """
