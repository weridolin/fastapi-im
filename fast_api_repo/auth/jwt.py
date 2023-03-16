import jwt
from typing import Dict
import datetime
from database.models.user import User
from fast_api_repo.settings import AppSettings
from fast_api_repo.auth.schema import JWTPayLoad
from pydantic import ValidationError

def create_jwt_token(
    *,
    jwt_content: Dict[str, str],
    secret_key: str,
    algorithm:str
) -> str:
    to_encode = jwt_content.copy()
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def create_access_token_for_user(user: User,app_setting:AppSettings) -> str:
    return create_jwt_token(
        jwt_content=JWTPayLoad(
            username=user.username,
            exp=datetime.timedelta(minutes=AppSettings.JWT_EXPIRE_TIME)
        ).dict(),
        secret_key=app_setting.JWT_KEY,
        algorithm=app_setting.JWT_ALGORITHM
    )


def get_payload_from_token(token: str,app_setting:AppSettings) -> JWTPayLoad:
    try:
        return JWTPayLoad(**jwt.decode(token, app_setting.JWT_KEY, algorithms=[AppSettings.JWT_ALGORITHM]))
    except jwt.PyJWTError as decode_error:
        raise ValueError("unable to decode JWT token") from decode_error
    except ValidationError as validation_error:
        raise ValueError("malformed payload in token") from validation_error