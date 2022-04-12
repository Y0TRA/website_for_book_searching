from django.contrib import admin

from .models import Book, WordsFreq

admin.site.register(Book)
# admin.site.register(WordsFreq)
# this model was not registered, but it works
