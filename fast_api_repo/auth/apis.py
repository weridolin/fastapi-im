from fastapi import APIRouter,Depends
from fast_api_repo.auth.schema import LoginRequest,LoginResponse,BaseResponse,UserWithToken
from database.repositories.user import UserRepository
from database.base import get_repository
from fast_api_repo.settings import get_app_settings,AppSettings
from fast_api_repo.utils import is_email
from database.exceptions import UserDoesNotExist,PassWordError
from starlette import status
from fast_api_repo.auth.jwt import create_access_token_for_user

auth_router = APIRouter()



@auth_router.post(
        "/login",
        name="auth:login",
        response_model=LoginResponse
    )
async def login(
        login_request:LoginRequest,
        users_repo:UserRepository=Depends(get_repository(UserRepository)),
        app_setting:AppSettings=Depends(get_app_settings)
    ):
    """
        登录接口
    """
    if is_email(login_request.count):
        user = await users_repo.get_user_by_email(email=login_request.count)
    else:
        user = await users_repo.get_user_by_username(username=login_request.count)
    if not user:
        raise UserDoesNotExist(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名不存在"
        )
    if user.password != login_request.password:
        raise PassWordError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码错误"
        ) 
    ## generate jwt
    access_token = create_access_token_for_user(user=user,app_setting=app_setting)
    return LoginResponse(
        message="登录成功",
        data = UserWithToken(
            access_token=access_token,
            username=user.username,
            
        )
    )


@auth_router.post(
    "/logout",
    name="auth:logout",
    response_model=BaseResponse
    )
def logout():
    """
        登出接口
    """
    ...



