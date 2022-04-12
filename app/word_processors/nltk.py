from nltk import pos_tag
from nltk.corpus import words
from nltk.tokenize import word_tokenize
from functools import cached_property
from .base import BaseAbstractWordProcessor


class NLTKWordProcessor(BaseAbstractWordProcessor):
    word_types = {"noun": ("NN", "NNS", "NNPS", "NNP")}

    @cached_property
    def _english_words(self) -> set:
        return set(words.words())

    def is_word_english(self, word: str) -> bool:
        return word in self._english_words

    def get_word_type_token(self, word: str) -> str:
        # https://www.geeksforgeeks.org/part-speech-tagging-stop-words-using-nltk-python/
        word_type_token = word_tokenize(word)
        return pos_tag(word_type_token)[0][1]
