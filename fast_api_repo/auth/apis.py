from fastapi import APIRouter
from fast_api_repo.auth.schema import LoginRequest,LoginResponse,BaseResponse
auth_router = APIRouter()


@auth_router.post(
    "/login",
    name="auth:login",
    response_model=LoginResponse
    )
def login(login_request:LoginRequest):
    """
        登录接口
    """
    ...


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



