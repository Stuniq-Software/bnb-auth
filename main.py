from fastapi import FastAPI
from controller import AuthController
from dtypes import APIResponse, HttpStatus
import os

if os.getenv("ENV", "dev") == "dev":
    from dotenv import load_dotenv

    load_dotenv()
    print("Development Environment\nLoading .env File")

app = FastAPI(
    title="Bnb Clone Auth Service",
    description="This is the authentication service for the Bnb Clone Application",
    version="0.1.1",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Abhiram B.S.N.",
        "email": "abhirambsn@gmail.com",
        "url": "https://abhirambsn.com",
    }
)

app.include_router(AuthController)


@app.get("/healthz")
async def health_check():
    api_response = APIResponse(status=HttpStatus.OK, data=None, message="ok")
    return api_response.to_dict()

@app.get("/")
async def health_check():
    api_response = APIResponse(status=HttpStatus.OK, data=None, message="ok")
    return api_response.to_dict()
