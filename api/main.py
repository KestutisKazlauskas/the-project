"""
Minimal FastAPI application taken directly from the tutorial.
https://fastapi.tiangolo.com/
"""
from typing import List
import logging
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

api = FastAPI()
logger = logging.getLogger(__name__)


class CreateWordRequest(BaseModel):
    words: List[str]


@api.get("/")
def index():
    return {"message": "Hello World"}


@api.post("/words.json")
def create(request: CreateWordRequest):
    return JSONResponse(request, status_code=status.HTTP_201_CREATED)


@api.get("/anagrams/{word}.json")
def get_anagrams(word: str, nouns: bool = None):
    # nouns param to include or exclude the nouns from anagrams
    return JSONResponse({"anagrams": [word]}, status_code=status.HTTP_201_CREATED)


@api.delete("/words/{word}.json")
def delete_word(word: str):
    logger.info(f"{word} deleted")
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)


@api.delete("/words.json")
def delete_word():
    logger.info(f"All words deleted")
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)


@api.get("/words/analytics.json")
def words_analytics():
    logger.info(f"Returns a count of words in the corpus and min/max/median/average word length")
    return JSONResponse({}, status_code=status.HTTP_200_OK)


@api.get("/anagrams/analytics.json")
def anagrams_analytics():
    logger.info(f"Return words with most anagrams")
    return JSONResponse({}, status_code=status.HTTP_200_OK)
