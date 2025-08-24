class InvalidEmail(Exception):
    pass


class PasswordTooShort(Exception):
    pass


class UserExists(Exception):
    pass


class UserDoesNotExists(Exception):
    pass


class PasswordTooLong(Exception):
    pass


class EmailTooLong(Exception):
    pass


class RateLimitError(Exception):
    pass


class AuthenticationError(Exception):
    pass
