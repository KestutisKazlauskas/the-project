from __future__ import annotations

import logging
from typing import List, TYPE_CHECKING

from ..models.words import Word

if TYPE_CHECKING:
    from ..word_processors.base import BaseAbstractWordProcessor
    from ..repositories.base import BaseAbstractWordsRepository

logger = logging.getLogger(__name__)


class WordService:
    def __init__(
            self,
            repo: BaseAbstractWordsRepository,
            processor: BaseAbstractWordProcessor
    ):
        self.repository = repo
        self.processor = processor

    def create_words(self, words: List[str]) -> List[Word]:
        words_to_create = []
        for word in words:
            if not self.processor.is_word_english(word):
                logger.info(f"{word} is not english")
                continue
            english_word = Word(word=word, word_type_token=self.processor.get_word_type_token(word))
            words_to_create.append(english_word)

        return self.repository.bulk_save(words_to_create) if words_to_create else words_to_create

    def list_anagrams_by_word(
        self, word_id: str, include_word_type: str = None, exclude_word_type: str = None, limit: int = None
    ) -> List[str]:
        word = self.repository.query_word_by_id(id_=word_id.lower())

        include_word_types = self.processor.word_types.get(include_word_type)
        exclude_word_types = self.processor.word_types.get(exclude_word_type)

        return self.repository.query_anagrams_by_word(word, include_word_types, exclude_word_types, limit)
