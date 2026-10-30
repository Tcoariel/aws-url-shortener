
import os
import uuid
from datetime import datetime, timezone

import boto3
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
TABLE_NAME = os.getenv("DYNAMODB_TABLE", "urls")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "*")
PUBLIC_API_BASE_URL = os.getenv(
    "PUBLIC_API_BASE_URL", "http://localhost:8000"
)


dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(TABLE_NAME)

app = FastAPI(title="URL Shortener API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN] if FRONTEND_ORIGIN != "*" else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLRequest(BaseModel):
    original_url: HttpUrl


@app.post("/shorten")
def shorten_url(data: URLRequest):

    short_code = str(uuid.uuid4())
    original_url = str(data.original_url)
    created_at = datetime.now(timezone.utc).isoformat()

    table.put_item(
        Item={
            "short_code": short_code,
            "original_url": original_url,
            "created_at": created_at
        }
    )

    short_url = f"{PUBLIC_API_BASE_URL}/{short_code}"

    return {
        "short_code": short_code,
        "original_url": original_url,
        "short_url": short_url
    }


@app.get("/{short_code}")
def redirect_url(short_code: str):

    response = table.get_item(
        Key={"short_code": short_code}
    )

    item = response.get("Item")

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Enlace no encontrado"
        )

    return RedirectResponse(
        url=item["original_url"],
        status_code=307
    )


@app.get("/urls/{short_code}")
def get_url(short_code: str):

    response = table.get_item(
        Key={"short_code": short_code}
    )

    item = response.get("Item")

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Enlace no encontrado"
        )

    return {
        "short_code": item["short_code"],
        "original_url": item["original_url"],
        "created_at": item["created_at"]
    }


@app.get("/")
def home():
    return {"message": "URL Shortener API funcionando"}
