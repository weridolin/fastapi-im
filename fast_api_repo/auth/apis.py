from fastapi import APIRouter,Depends
from fast_api_repo.auth.schema import LoginRequest,LoginResponse,BaseResponse,UserWithToken,RegisterForm,UserSchema
from database.repositories.user import UserRepository
from database.base import get_repository
from settings import get_app_settings,AppSettings
from fast_api_repo.utils import is_email
from database.exceptions import UserDoesNotExist,PassWordError,EmailIsExistError,UserIsExistError
from starlette import status
from database.jwt import create_access_token_for_user,get_current_active_user
from fast_api_repo.auth.encrypt import encrypt_by_md5
from database.models.user import User

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
    if user.password != encrypt_by_md5(login_request.password,app_setting.SALT):
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
async def logout(
        current_user: User = Depends(get_current_active_user)
    ):
    """
        登出接口
    """
    return BaseResponse(
        message="注销成功",
        status_code=status.HTTP_204_NO_CONTENT,
        data=None
    )


@auth_router.post(
    "/register",
    name="auth:register",
    response_model=BaseResponse
)
async def register(
    register_form:RegisterForm,
    users_repo:UserRepository=Depends(get_repository(UserRepository)),
    app_setting:AppSettings=Depends(get_app_settings)
):
    """
        注册接口
    """
    # check username is used
    if await users_repo.get_user_by_username(username=register_form.username):
        raise UserIsExistError(
            detail="用户名已经存在",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if await users_repo.get_user_by_email(email=register_form.email):
        raise EmailIsExistError(
            detail="邮箱已经存在",
            status_code=status.HTTP_400_BAD_REQUEST
        )        
    
    user = await users_repo.create_user(salt=app_setting.SALT,**register_form.dict())
    return BaseResponse(
        message="创建成功",
        data=UserSchema.from_orm(user).dict()
    )