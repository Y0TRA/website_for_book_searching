from django.shortcuts import render
from django.http import HttpResponse

from .analyze import *


def main_page(request):
    return render(request, 'websearch/index.html', {})


def results_page(request):
    text = request.POST['text']
    books = search(text)

    return render(request, 'websearch/results.html', {'books': books})


def admin_page(request):
    return render(request, 'websearch/admin.html', {})


def admin_save_page(request):
    add(request)

    return render(request, 'websearch/admin.html', {})
