from fastapi import HTTPException


class LoginRequiredException(HTTPException):
    """Login"""


class InvalidUserIdException(Exception):
    """Invalid User ID"""


class UserHasAccoutException(Exception):
    "User has already account"


class InvalidEmailException(Exception):
    "Invalid email"



