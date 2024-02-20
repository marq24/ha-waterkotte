class InvalidValueException(Exception):
    """A InvalidValueException."""

    # pass


class InvalidResponseException(Exception):
    """A InvalidResponseException."""

    # pass


class StatusException(Exception):
    """A Status Exception."""

    # pass


class TooManyUsersException(StatusException):
    """A TooManyUsers Exception."""
    # pass

class Http404Exception(Exception):
    """A HTTP404 Exception."""
    # pass

