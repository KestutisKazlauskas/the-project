from __future__ import annotations

import logging
from typing import List
from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch.helpers import bulk

from ..exceptions import WordNotFound
from ..repositories.base import BaseAbstractWordsRepository


from ..models.words import Word, AggregatedWordsData

logger = logging.getLogger(__name__)


class ElasticSearchRepository(BaseAbstractWordsRepository):
    _index_name = "words"

    def __init__(self, es_client: Elasticsearch):
        self.es_client = es_client

    @staticmethod
    def _make_term_query_from_list(terms: List[str]) -> dict:
        return {"terms": {"word_type": [term.lower() for term in terms]}}

    def bulk_save(self, words: List[Word]) -> List[Word]:
        logger.info("ElasticSearchRepository.bulk_save started")
        words_to_persist = []
        word_index_by_id = {}
        for index, word in enumerate(words):
            words_to_persist.append({
                "_index": self._index_name,
                "_id": word.word,
                "_source": {
                    "word": word.word,
                    "length": word.length,
                    "word_type": word.word_type_token,
                    "anagram_token": word.anagram_token,
                }
            })
            word_index_by_id[word.word] = index
        success, errors = bulk(self.es_client, words_to_persist)

        # Remove words if was not saved to elastic
        for error in errors:
            word_id = error["_id"]
            del words[word_index_by_id[word_id]]

        return words

    def query_anagrams_by_word(
        self,
        word: Word,
        include_word_types: List[str] = None,
        exclude_word_types: List[str] = None,
        limit: int = None
    ) -> List[str]:
        query = {
            "bool": {
                "filter": [
                    {"term": {"anagram_token": word.anagram_token}},
                ],
                "must_not": [
                    {"term": {"word": word.word}},
                ]
            }
        }
        if include_word_types:
            query["bool"]["filter"].append(self._make_term_query_from_list(include_word_types))
        if exclude_word_types:
            query["bool"]["must_not"].append(self._make_term_query_from_list(exclude_word_types))

        logger.info(f"Elastic serach query: {query}")
        resp = self.es_client.search(index="words", query=query, fields=["word"], source=False, size=limit)
        logger.info(resp)
        words = []
        for hit in resp['hits']['hits']:
            words.append(hit["fields"]["word"][0])

        return words

    def query_word_by_id(self, id_: str) -> Word:
        try:
            resp = self.es_client.get(index=self._index_name, id=id_)
        except NotFoundError as err:
            logger.info(f"response {err}")
            raise WordNotFound(f"{id_} not found")

        word = resp["_source"]
        return Word(
            word=word.get("word"),
            word_type_token=word.get("word_type"),
            length=word.get("length"),
            anagram_token=word.get("anagram_token")
        )

    def delete_word_by_id(self, id_: str):
        try:
            self.es_client.delete(index=self._index_name, id=id_)
        except NotFoundError as err:
            logger.info(f"response {err}")
            raise WordNotFound(f"{id_} not found")

    def delete_all_words(self):
        try:
            self.es_client.indices.delete(index=self._index_name)
        except NotFoundError as err:
            logger.info(f"response {err}")
            raise WordNotFound(f"Not Found")

    def aggregate_words_data(self) -> AggregatedWordsData:
        """
        Method for returning data of count/min/max/median/average word length
        """
        field = {"field": "length"}
        aggregations = {
            "sum_length": {"sum": field},
            "min_length": {"min": field},
            "max_length": {"max": field},
            "avg_length": {"avg": field},
            "total_words": {"value_count": field}
        }
        logger.info(f"Aggregation query {aggregations}")
        resp = self.es_client.search(aggregations=aggregations, size=0)
        logger.info(f"Aggregation response {resp}")

        data = resp.get("aggregations", {})
        median_length = round(data["sum_length"]["value"] / data["total_words"]["value"], 2)
        return AggregatedWordsData(
            total_words=data["total_words"]["value"],
            min_length=data["min_length"]["value"],
            max_length=data["max_length"]["value"],
            avg_length=data["avg_length"]["value"],
            median_length=median_length
        )
