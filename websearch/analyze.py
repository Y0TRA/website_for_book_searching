from nltk import sent_tokenize, regexp_tokenize
from nltk.corpus import stopwords
import pymorphy2
import sqlite3 as sql

# TODO: ограничение не маленькие значения слов
# TODO: поиск по синонимам
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

    return wordfreq


def search(text, min_volume=None, max_volume=None, min_year=None, max_year=None, rating=None, age_limit=None):
    query = WordsFreq.objects.all()

    if min_volume is not None:
        query = query.filter(volume__gte=min_volume)
    if max_volume is not None:
        query = query.filter(volume__lte=max_volume)
    if min_year is not None:
        query = query.filter(year__gte=min_year)
    if max_year is not None:
        query = query.filter(year__lte=max_year)

    # TODO: rating and age_limit

    input_text_data = tf(text)

    all_matches_docs = {}

    for key in input_text_data.keys():
        books = query.filter(word=key)
        for book in books:
            if book.book_id not in all_matches_docs.keys():
                all_matches_docs[book.book_id] = book.word_freq
            else:
                all_matches_docs[book.book_id] = all_matches_docs[book.book_id] + book.word_freq

    sorted_tuple = sorted(all_matches_docs.items(), key=lambda x: x[1])[::-1]

    print("FREQ INFO:", sorted_tuple)

    return dict(sorted_tuple).keys()


def add(request):
    # TODO: обработка исключений
    print( request.POST)
    for value in request.POST.values():
        if value == '':
            print("The field is not filled")
            return

    if request.FILES['file'] == '':
        print("The field is not filled")
        return


    post_data = request.POST
    file = request.FILES['file']

    # TODO: кажется, тут проблема с кодировкой
    try:
        text = file.read().decode('utf-8')
    except:
        try:
            text = file.read().decode('utf-16')
        except:
            print("Can't open file")
            return

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
