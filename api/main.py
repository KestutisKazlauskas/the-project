"""
Minimal FastAPI application taken directly from the tutorial.
https://fastapi.tiangolo.com/
"""

from fastapi import FastAPI

api = FastAPI()


@api.get("/")
def read_root():
    return {"message": "Hello World"}
