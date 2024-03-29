import csv

from nltk import sent_tokenize, regexp_tokenize
from nltk.corpus import stopwords
import pymorphy2
import requests
import json

from .models import Book, WordsFreq

stopwords_ru = stopwords.words("russian")


def normalize_tokens(tokens):
    morph = pymorphy2.MorphAnalyzer()
    return [morph.parse(tok)[0].normal_form for tok in tokens]


def remove_stopwords(tokens, stopwords=None, min_length=4):
    if not stopwords:
        return tokens
    stopwords = set(stopwords)
    tokens = [tok
              for tok in tokens
              if tok not in stopwords and len(tok) >= min_length]
    return tokens


def tokenize_n_lemmatize(
        text, stopwords=None, normalize=True,
        regexp=r'(?u)\b\w{4,}\b'):
    words = [w for sent in sent_tokenize(text)
             for w in regexp_tokenize(sent, regexp)]
    if normalize:
        words = normalize_tokens(words)
    if stopwords:
        words = remove_stopwords(words, stopwords)
    return words


def tf(text):
    tokens = tokenize_n_lemmatize(text, stopwords=stopwords_ru)
    amount = len(tokens)
    wordfreq = {}
    for token in tokens:
        if token not in wordfreq.keys():
            wordfreq[token] = 1
        else:
            wordfreq[token] += 1

    for key in wordfreq.keys():
        wordfreq[key] = wordfreq[key] / amount

    for key in list(wordfreq.keys()):
        if wordfreq[key] < 0.00003:
            del wordfreq[key]
    return wordfreq


def get_synonyms(word):
    synonyms = []
    data = requests.get(f"http://www.serelex.org/find/ru-skipgram-librusec/{word}").text

    data = json.loads(data)

    if data["totalRelations"] > 0:
        for key in data["relations"]:
            synonyms.append(key["word"])

    return synonyms


def search(request):
    post_data = request
    print(post_data)

    books_list = Book.objects.all()

    if post_data['min_volume'] != "":
        books_list = books_list.filter(volume__gte=post_data['min_volume'])
    if post_data['max_volume'] != "":
        books_list = books_list.filter(volume__lte=post_data['max_volume'])
    if post_data['min_year'] != "":
        books_list = books_list.filter(year__gte=post_data['min_year'])
    if post_data['max_year'] != "":
        books_list = books_list.filter(year__lte=post_data['max_year'])
    if post_data.get('age') is not None:
        books_list = books_list.filter(age_limit__in=post_data.getlist('age'))
    if post_data.get('rating') is not None:
        books_list = books_list.filter(rating__in=post_data.getlist('rating'))

    input_text_data = tf(post_data['text'])

    input_words_with_synonyms = list(input_text_data.keys())
    for word in input_text_data.keys():
        input_words_with_synonyms += get_synonyms(word)

    all_matches_docs = {}

    query = WordsFreq.objects.filter(book_id__in=books_list)

    for key in input_words_with_synonyms:
        books = query.filter(word=key)
        for book in books:
            if book.book_id not in all_matches_docs.keys():
                all_matches_docs[book.book_id] = book.word_freq
            else:
                all_matches_docs[book.book_id] = all_matches_docs[book.book_id] + book.word_freq

    sorted_tuple = sorted(all_matches_docs.items(), key=lambda x: x[1])[::-1]

    # print("FREQ INFO:", sorted_tuple)

    return dict(sorted_tuple).keys()


def add(request):
    # TODO: обработка исключений
    print(request.POST)
    post_data = request.POST

    files = request.FILES.getlist('file')
    print(files)
    if len(files) > 1:
        add_multiple(files)
        return
    else:
        file = files[0]

    if post_data["book"] == "":
        print("The field is not filled")
        return

    if post_data["author"] == "":
        print("The field is not filled")
        return

    if post_data["year"] == "":
        print("The field is not filled")
        return

    try:
        text = file.read().decode('utf-8')
    except BaseException:
        raise Exception('Ошибка кодировки файла')

    print("Successfully open file")

    new_book = Book(name=post_data["book"],
                    author=post_data["author"],
                    rating=post_data["rating"],
                    volume=post_data["volume"],
                    year=post_data["year"],
                    age_limit=post_data["age"],
                    annotation=post_data["annotation"])

    new_book.save()

    data = tf(text)

    print("Start inserting words...")
    for key in data.keys():
        WordsFreq(book_id=new_book, word=key, word_freq=data[key]).save()
    print("Successfully insert")


def add_multiple(files):
    files_info = {}

    for f in files:
        if ".csv" in f.name:
            csv_file = f.read().decode('utf-8').split("\n")[1:]
            for line in csv_file:
                fields = line.split(";")
                files_info[fields[0]] = fields[1:]

    print(files_info.keys())
    for file in files:
        if ".csv" not in file.name:
            file_text = file.read().decode('utf-8')
            add_one(file.name.replace(".txt", ""), files_info[file.name.replace(".txt", "")], file_text)


def add_one(name, file_info, file_text):
    print(file_info)
    new_book = Book(name=name,
                    author=file_info[0],
                    rating=file_info[1],
                    year=file_info[2],
                    age_limit=file_info[3],
                    annotation=file_info[4],
                    volume=len(file_text.split(" ")))
    new_book.save()
    data = tf(file_text)
    print("Start inserting words...")
    for key in data.keys():
        WordsFreq(book_id=new_book, word=key, word_freq=data[key]).save()
    print("Successfully insert")
