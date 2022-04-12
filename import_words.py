import os
os.getcwd()

from app.deps import get_repo, get_word_processor
from app.services.words import WordService

service = WordService(repo=get_repo(), processor=get_word_processor())


def parse_dictionary_file(file: str):
    with open(file, 'r') as f:
        data = []
        while True:
            line = f.readline()
            if not line:
                break  # done
            data.append(line. rstrip("\n"))
            if len(data) == 500:
                yield data
                data = []

        if data:
            yield data


def run():
    for words in parse_dictionary_file("dictionary.txt"):
        service.create_words(words=words)


if __name__ == "__main__":
    run()