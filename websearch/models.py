from dataclasses import Field

from django.db import models


class Book(models.Model):
    name = models.CharField(max_length=70)
    author = models.CharField(max_length=70)
    rating = models.IntegerField()
    volume = models.IntegerField(null=True, default=None)
    annotation = models.TextField()
    year = models.IntegerField()
    age_limit = models.IntegerField(default=0)


class WordsFreq(models.Model):
    book_id = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='words_freq')
    word = models.CharField(max_length=70)
    word_freq = models.FloatField()