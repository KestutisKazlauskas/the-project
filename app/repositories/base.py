from abc import ABC, abstractmethod
from typing import List

from ..models.words import Word, AggregatedWordsData


class BaseAbstractWordsRepository(ABC):
    @abstractmethod
    def bulk_save(self, words: List[Word]) -> List[Word]:
        raise NotImplemented

    @abstractmethod
    def query_anagrams_by_word(
        self,
        word: Word,
        include_word_types: List[str] = None,
        exclude_word_types: List[str] = None,
        limit: int = None
    ) -> List[str]:
        raise NotImplemented

    @abstractmethod
    def query_word_by_id(self, id_: str) -> Word:
        raise NotImplemented

    @abstractmethod
    def delete_word_by_id(self, id_: str):
        raise NotImplemented

    @abstractmethod
    def delete_all_words(self):
        raise NotImplemented

    @abstractmethod
    def aggregate_words_data(self) -> AggregatedWordsData:
        """
        Method for returning data of count/min/max/median/average word length
        """
        raise NotImplemented
