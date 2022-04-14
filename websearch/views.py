from django.shortcuts import render
from django.http import HttpResponse

from .analyze import *


def main_page(request):
    books = []
    if request.POST.get('text') is not None:
        books = search(request.POST)

    return render(request, 'websearch/index.html', {'books': books})


def results_page(request):
    books = search(request.POST)

    return render(request, 'websearch/results.html', {'books': books})


def admin_page(request):
    return render(request, 'websearch/admin.html', {})


def admin_save_page(request):
    add(request)

    return render(request, 'websearch/admin.html', {})
