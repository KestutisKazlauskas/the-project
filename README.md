# Anagrams api

API that allows fast searches for [anagrams](https://en.wikipedia.org/wiki/Anagram)

## Prerequisites

- Docker version 20.10.10 and up
- docker-compose version 1.29.2 and up

## How to run locally

To run the api on your computer need to:

1. Clone the repo `git clone git@github.com:KestutisKazlauskas/the-project.git`
2. In project main directory run command: `docker-compose up`
3. Optionally for all  english words data insertion to data store could run command `docker-compose exec api python import_words.py` for testing anagrams search performacne of real word case.
4. Api docs could be reach: [http://localhost:8000](http://localhost:8000)

## Implementation details

For api implementation I choose to use:
- [ElasticSearch](https://www.elastic.co/what-is/elasticsearch) as search engine for fast querying the data. 
In this case I also use it as a data store as the data is not critical and could be imported from dictonary.txt if where would be data loss for some kind of reason.
However I would not use it in the real world for data store purpose scenario if the api would have critical data and for example user functionality.
In this kind of situation I would use it together with some kind SQL database such as Postgres for storing the data and the elastic search for indexing data and seraching it.
Postgres is proper [ACID](https://en.wikipedia.org/wiki/ACID) data store as elastic search is not. ElasticSearch is design for fast text searching.
- [FastApi](https://fastapi.tiangolo.com/) for api layer of the app. It is minimal and flexible framework with openapi docs implemented out of th box. 
The frameworks seems a good fit for the use case as the project scope was not very big and would need to custom datastore. 
Plus It is a good place for me to play around with the new technology.
- [NLTK](https://www.nltk.org/) - for checking if provided word is english and for extracting the part of speech for the word.
- [Poetry](https://python-poetry.org/) for python dependency management.
- [Docker and docker-compose](https://docs.docker.com/compose/install/) for containerizing the app and developing it locally for predictable environment.

### Some thoughts on current implementation

- Current implementation do not fully validate inputs data. For example right now there is no limit how much words user could send for creating the words. 
In reality there is some limit on request body that user could send (depends on the system configs of course).
- Search api that returns anagrams with nouns current implementation is that word has only one speech of part. In reality the same word could be 
different part of speech depending on context. Probably would need to store all possible part of speech for the word and filtering based on all possible parts of that particular word.
- Have a little problem of thinking the structure of /anagrams/words.json(take words as parameter and returns if all fo those words are anagrams).
As api results should return true or false it seems like this api should be more as [RPC](https://en.wikipedia.org/wiki/Remote_procedure_call) style of api. 
The current solution was to add PUT api to /anagrams/words.js as it adding data to the resource entity(updating it) and returning the result.
Other solution could be to make separate from anagrams api that would be dedicated to run rpc style of api: `POST /command/check_words_is_anagrams` which return true or false with status 200. 

### Project structure

- **app** main directory of FastApi app
  - **models** - data and logic layer object implementation some kind of domain part. 
    - **words.py** - Word object implementation.
  - **repositories** - logic for storing the words to data store
    - **base.py** - abstract class for logic
    - **elasticserach.py** concrete implementation for elasticsearch store
  - **routes** fast api controllers for the app.
    - **anagrams.py** anagrams api
    - **index.py** main route redirects to api docs in local case `http://localhost:8000/`
    - **words.py** words api 
  - **services** - class for storing logic that requires connecting models, word_processors and repositories together.
    - **words.py** - create and search anagrams of words logic implementation.
  - **word_processors** - classes for implementing logic for dealing with words logic such as checking is the word is english, finding out the word part of speach
    - **base.py** - abstract class for implemented logic 
    - **nltk.py** - concrete implementation of the logic. The files instance are initiated in deps.py file and pass to Fast api routes.
  - **deps.py** - dependencies for be able to run the app. the dependencies are passed to Fast api routes.
  - **exceptions.py** - custom app exceptions that could be raised with in the app
  - **main.py** - main script for running FastApi app. Here goes all app configs.
  - **settings.py** - file for storing settings for the project which is take from environment variables
- **config** - directory for storing config files like `logger.conf` use for logger formatting.
- **docker** - directory for storing docker files for image building
- **import_words.py** - script for importing the `dictionary.txt` file to elastricsearch data store. for testing search api

## Features that could be added

- User authentication authorization 
  - some apis like create/delete actions could be allowed only admin users other apis like anagrams search could be public
  - or all apis could be separated by users - one user could execute all apis, but words will be visible for that user and the users that he/she allows to call apis
- Add api versioning. Because api could be public and used by a lot of clients it is a good practice to add 
the api versioning. Versioning could be added in the url like `/v1/words.json` or query params like `words.json?version=1`. 
Also versioning could be done by using headers like `Accept: application/vnd.example+json;version=1.0` or custom ones.