import logging
from os import getenv
from typing import List

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import nltk
from nltk.tokenize import word_tokenize

api = FastAPI()
es = Elasticsearch(getenv("ELASTICSEARCH_HOSTS"), timeout=60*60)

logging.config.fileConfig("config/logger.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

word_types = {
    "noun": ["NN", "NNS", "NNPS", "NNP"]
}


@api.on_event("startup")
async def start_up():
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')


@api.on_event("shutdown")
async def shut_down():
    es.close()


class CreateWordRequest(BaseModel):
    words: List[str]


@api.get("/")
def index():
    text = "India"
    token = word_tokenize(text)
    ans = nltk.pos_tag(token)
    logger.info(ans)
    return {"message": "Hello World"}


@api.post("/words.json")
def create(request: CreateWordRequest):
    # TODO validate if word exists!
    logger.info("Creating the words")
    words = []
    for word in request.words:
        word_type_token = word_tokenize(word)
        word_type = nltk.pos_tag(word_type_token)[0][1]
        words.append({
            "_index": "words",
            "_id": word,
            "_source": {
                "word": word,
                "length": len(word),
                "word_type": word_type,
                "anagram_token": "".join(sorted(word))
            }
        })
    response = bulk(es, words)
    logger.info(response)
    logger.info("Words created")
    return JSONResponse(request.dict(), status_code=status.HTTP_201_CREATED)


@api.get("/anagrams/{word}.json")
def get_anagrams(word: str, nouns: bool = None):
    # nouns param to include or exclude the nouns from anagrams
    anagram_token = "".join(sorted(word))
    query = {
        "bool": {
            "must": [
                    {"match": {"anagram_token":   anagram_token}},
                ],
            "must_not": [
                {"match": {"word": word}},
            ]
        }
    }
    resp = es.search(index="words", query=query)
    words = []
    for hit in resp['hits']['hits']:
        words.append(hit["_source"]["word"])
    logger.info(resp)
    return JSONResponse({"anagrams": words}, status_code=status.HTTP_200_OK)


@api.delete("/words/{word}.json")
def delete_word(word: str):
    es.delete(index="words", id=word, ignore=[404])
    logger.info(f"{word} deleted")
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)


@api.delete("/words.json")
def delete_word():
    es.indices.delete(index='words', ignore=[404])
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
