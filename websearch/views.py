from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse_lazy

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


class LoginUser(LoginView):
    form_class = AuthenticationForm
    template_name = 'websearch/login.html'

    def get_success_url(self):
        return reverse_lazy('admin_page')
