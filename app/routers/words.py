import logging
from typing import List

from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.deps import get_repo, get_word_processor
from app.services.words import WordService
from app.exceptions import WordNotFound
from app.models.words import AggregatedWordsData

logger = logging.getLogger(__name__)

es = None

router = APIRouter()


class CreateWordRequest(BaseModel):
    words: List[str]


create_api_description = """
`POST /words.json`: Takes a JSON array of English-language words and adds them to the corpus for fast anagrams search
"""


@router.post("/words.json", description=create_api_description, name="Insert English words for anagrams search")
def create(request: CreateWordRequest, repo=Depends(get_repo), processor=Depends(get_word_processor)):

    logger.info(f"Create api reqeust {request}")
    created = WordService(repo=repo, processor=processor).create_words(request.words)
    logger.info(f"Words created: {created}")

    return JSONResponse([word.dict() for word in created], status_code=status.HTTP_201_CREATED)


delete_word_api_description = """
`DELETE /words/{word}.json`: Deletes a single word from the data store.
"""


@router.delete("/words/{word}.json", description=delete_word_api_description, name="Delete specific word from search")
def delete_word(word: str, repo=Depends(get_repo)):
    try:
        repo.delete_word_by_id(id_=word.lower())
    except WordNotFound as err:
        logger.info(f"{word} not found")
        raise HTTPException(status_code=404, detail=[{"msg": str(err)}])

    logger.info(f"{word} deleted")
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)


delete_words_api_description = """
`DELETE /words.json`: Deletes all contents of the data store.
"""


@router.delete("/words.json", description=delete_words_api_description, name="Delete all words")
def delete_words(repo=Depends(get_repo)):
    try:
        repo.delete_all_words()
    except WordNotFound as err:
        logger.info(f"Words deleted")
        raise HTTPException(status_code=404, detail=[{"msg": str(err)}])

    logger.info(f"All words deleted")
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)


word_analytics_api_description = """
Api that returns a count of words in the corpus and min/max/median/average word length
"""


@router.get(
    "/words/analytics.json",
    response_model=AggregatedWordsData,
    description=word_analytics_api_description,
    name="Analytics of Words"
)
def words_analytics(repo=Depends(get_repo)):
    data = repo.aggregate_words_data()
    return JSONResponse(data.dict(), status_code=status.HTTP_200_OK)
