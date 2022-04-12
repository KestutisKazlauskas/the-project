from elasticsearch import Elasticsearch

from .settings import settings
from .repositories.elasticsearch import ElasticSearchRepository
from .word_processors.nltk import NLTKWordProcessor

es_client = Elasticsearch(
    settings.ELASTICSEARCH_HOSTS,
    timeout=settings.ELASTICSEARCH_TIME_OUT,
    max_retries=settings.ELASTICSEARCH_MAX_RETRIES,
)
word_repository = ElasticSearchRepository(es_client=es_client)
word_processor = NLTKWordProcessor()


def get_repo():
    return word_repository


def get_word_processor():
    return word_processor
