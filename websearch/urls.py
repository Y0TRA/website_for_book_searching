from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('results', views.results_page, name='results_page'),
    path('admin', views.admin_page, name='admin_page'),
    path('admin_save', views.admin_save_page, name='admin_save_page'),
]
