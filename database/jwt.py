from typing import Dict
import datetime
from database.models.user import User
from settings import AppSettings
from fast_api_repo.auth.schema import JWTPayLoad
from pydantic import ValidationError
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from database.repositories.user import UserRepository
from database.exceptions import UserDoesNotExist
from fast_api_repo.auth.encrypt import encrypt_by_md5
from fastapi import status
from typing import Optional
from fastapi import Depends
from jose import JWTError,jwt
from database.base import get_repository,get_app_settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_jwt_token(
    *,
    jwt_content: Dict[str, str],
    secret_key: str,
    algorithm:str
) -> str:
    to_encode = jwt_content.copy()
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def create_access_token_for_user(user: User,app_setting:AppSettings) -> str:
    jwt_content=JWTPayLoad(
        username=user.username,
        user_id=user.id,
        exp=(datetime.datetime.utcnow()+datetime.timedelta(minutes=app_setting.JWT_EXPIRE_TIME)).timestamp()
    ).dict()
    print(jwt_content)
    return create_jwt_token(
        jwt_content=jwt_content,
        secret_key=app_setting.JWT_KEY,
        algorithm=app_setting.JWT_ALGORITHM
    )


def get_payload_from_token(app_setting:AppSettings,token:str = Depends(oauth2_scheme)) -> JWTPayLoad:
    # try:
    return JWTPayLoad(**jwt.decode(token, app_setting.JWT_KEY, algorithms=[app_setting.JWT_ALGORITHM]))
    # except JWTError as decode_error:
    #     print(decode_error)
    #     raise ValueError("unable to decode JWT token") from decode_error
    # except ValidationError as validation_error:
    #     raise ValueError("malformed payload in token") from validation_error
    

async def get_user_from_token(
        user_repo:UserRepository=Depends(get_repository(UserRepository)),
        app_setting:AppSettings=Depends(get_app_settings),
        token: str = Depends(oauth2_scheme)) -> User:
    payload:JWTPayLoad = get_payload_from_token(
        token=token,
        app_setting=app_setting
    )
    return await user_repo.get_user_by_user_id(user_id=payload.user_id)


async def authenticate_user(user_repo:UserRepository,app_setting:AppSettings,token: str = Depends(oauth2_scheme)):
    try:   
        user = await get_user_from_token(
            user_repo=user_repo,
            app_setting=app_setting,
            token=token)
        if not user:
            raise UserDoesNotExist(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="token不合法,找不到用户!",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except JWTError:
        raise UserDoesNotExist(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="token不合法,找不到用户!",
                headers={"WWW-Authenticate": "Bearer"},
            )  

async def get_current_active_user(current_user:User = Depends(get_user_from_token)):
    # if current_user.disabled:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
