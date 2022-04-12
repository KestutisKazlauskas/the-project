from dataclasses import dataclass
from pydantic import BaseModel


class AggregatedWordsData(BaseModel):
    total_words: int
    min_length: int
    max_length: int
    avg_length: float
    median_length: float


@dataclass()
class Word:

    word: str
    word_type_token: str
    length: int = None
    anagram_token: str = None

    def __post_init__(self):
        self.word = self.word.lower()

        if not self.length:
            self.length = len(self.word)

        if not self.anagram_token:
            self.anagram_token = "".join(sorted(self.word))

    def dict(self) -> dict:
        return {
            "word": self.word,
            "length": self.length,
            "word_type_token": self.word_type_token,
            "anagram_token": self.anagram_token
        }
