
from fastapi import HTTPException


class EntityDoesNotExist(Exception):pass

class UserDoesNotExist(HTTPException):pass

class PassWordError(HTTPException):pass

class UserIsExistError(HTTPException):pass

class EmailIsExistError(HTTPException):pass