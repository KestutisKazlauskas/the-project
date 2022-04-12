import nltk
from fastapi import FastAPI, APIRouter

from .routers import index, words, anagrams

description = """
---

An API that allows insert English words for fast searches for 
[anagrams](https://en.wikipedia.org/wiki/Anagram) of those words.
"""

app = FastAPI(
    title="Anagram api 🚀",
    description=description
)

api_router = APIRouter()
api_router.include_router(index.router)
api_router.include_router(words.router, tags=["words"])
api_router.include_router(anagrams.router, tags=["anagrams"])

app.include_router(api_router)


@app.on_event("startup")
async def start_up():
    nltk.download('words')
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')


