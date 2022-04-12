import logging
from typing import List
from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.services.words import WordService
from app.deps import get_repo, get_word_processor
from app.exceptions import WordNotFound

logger = logging.getLogger(__name__)

router = APIRouter()


class CheckWordsAnagramsRequest(BaseModel):
    words: List[str]


class CheckWordsAnagramsResponse(BaseModel):
    is_anagrams: bool
    words: List[str]


get_anagrams_by_word_api_description = """
 `GET /anagrams/{word}.json`: 
  - Returns a JSON array of English-language words that are anagrams of the word passed in the URL.  
  - This endpoint should support an optional query param that indicates the maximum number of results to return.
  - Respect a query param (nouns) for whether or not to include proper nouns in the list of anagrams.
"""


@router.get("/anagrams/{word}.json", description=get_anagrams_by_word_api_description, name="Search Anagrams of word")
def anagrams(
    word: str,
    nouns: bool = None,
    limit: int = None,
    repo=Depends(get_repo),
    processor=Depends(get_word_processor)
):
    # nouns param to include or exclude the nouns from anagrams
    noun_type = "noun"
    include_word_type = noun_type if nouns is True else None
    exclude_word_type = noun_type if nouns is False else None

    try:
        words = WordService(repo=repo, processor=processor).list_anagrams_by_word(
            word, include_word_type=include_word_type, exclude_word_type=exclude_word_type, limit=limit
        )
    except WordNotFound as err:
        raise HTTPException(status_code=404, detail=[{"msg": str(err)}])

    return JSONResponse({"anagrams": words}, status_code=status.HTTP_200_OK)


all_words_anagrams_api_description = """
Api that takes a set of words and returns whether or not they are all anagrams of each other
"""


@router.put(
    "/anagrams/words.json",
    response_model=CheckWordsAnagramsResponse,
    description=all_words_anagrams_api_description,
    name="Is anagrams?"
)
def all_words_anagrams(request: CheckWordsAnagramsRequest, processor=Depends(get_word_processor)):

    unique = list(set(request.words))
    if len(unique) < 2:
        raise HTTPException(status_code=400, detail=[{"msg": f"Need at least two unique words"}])

    words = []
    for word in unique:
        if not processor.is_word_english(word):
            raise HTTPException(status_code=400, detail=[{"msg": f"{word} is not english"}])
        words.append("".join(sorted(word.lower())))
    is_anagrams = all(words[0] == word for word in words)

    return JSONResponse(
        CheckWordsAnagramsResponse(is_anagrams=is_anagrams, words=request.words).dict(),
        status_code=status.HTTP_200_OK
    )
