from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from dtypes import APIResponse, HttpStatus
from repository import AuthRepository
from util import JWTHandler, Database, RedisSession
import base64
import os

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
auth_service = AuthRepository(
    jwt_handler=JWTHandler(secret=os.getenv("JWT_SECRET")),
    db_session=Database(),
    redis_session=RedisSession()
)


@router.post("/", response_model=APIResponse[dict])
async def create_user(request: Request, response: Response):
    body = await request.json()
    success, error = await auth_service.create_user(
        email=body.get("email"),
        password=body.get("password"),
        first_name=body.get("first_name"),
        last_name=body.get("last_name"),
        phone=body.get("phone"),
        line1=body.get("line1"),
        line2=body.get("line2"),
        city=body.get("city"),
        state=body.get("state"),
        country=body.get("country"),
        postal_code=body.get("postal_code"),
        account_type=body.get("account_type")
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error)
    api_response = APIResponse(data=body, message="User created successfully", status=HttpStatus.CREATED)
    response.status_code = status.HTTP_201_CREATED
    return api_response.to_dict()


@router.get("/token", response_model=APIResponse[dict])
async def get_token(request: Request, response: Response):
    auth_header = request.headers.get("Authorization", None)
    if not auth_header:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header not found")

    auth_type, auth_value = auth_header.split(" ")
    if auth_type.lower() != "basic":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization type")

    username, password = base64.b64decode(auth_value).decode("utf-8").split(":")
    data, error = await auth_service.login_user(email=username, password=password)
    if error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error)

    api_response = APIResponse(data=data, message="Token generated successfully", status=HttpStatus.OK)
    response.status_code = status.HTTP_200_OK
    return api_response.to_dict()


@router.get("/verify", response_model=APIResponse[dict])
async def validate(request: Request, response: Response):
    auth_header = request.headers.get("Authorization", None)
    if not auth_header:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header not found")

    auth_type, token = auth_header.split(" ")
    if auth_type.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization type")

    data, error = await auth_service.verify_user(token)
    if error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error)

    api_response = APIResponse(data=data, message="Token is valid", status=HttpStatus.OK)
    response.status_code = status.HTTP_200_OK
    return api_response.to_dict()


@router.post("/refresh", response_model=APIResponse[dict])
async def refresh(request: Request, response: Response):
    auth_header = request.headers.get("Authorization", None)
    if not auth_header:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header not found")

    auth_method, token = auth_header.split(" ")
    if auth_method.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization method")

    body = await request.json()
    access_token, refresh_token = await auth_service.refresh_token(
        access_token=token,
        refresh_token=body.get("refresh_token")
    )
    if access_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=refresh_token)
    api_response = APIResponse(
        data={"access_token": access_token, "refresh_token": refresh_token},
        message="Token refreshed successfully",
        status=HttpStatus.OK
    )
    response.status_code = status.HTTP_200_OK
    return api_response.to_dict()
