from abc import ABC, abstractmethod


class BaseAbstractWordProcessor(ABC):
    @abstractmethod
    def is_word_english(self, word: str) -> bool:
        raise NotImplemented

    @abstractmethod
    def get_word_type_token(self, word: str) -> str:
        raise NotImplemented

    @property
    @abstractmethod
    def word_types(self) -> dict:
        raise NotImplemented

