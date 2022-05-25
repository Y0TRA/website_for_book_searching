from django.urls import path
from . import views
from .views import LoginUser

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('results', views.results_page, name='results_page'),
    path('admin', views.admin_page, name='admin_page'),
    path('admin_save', views.admin_save_page, name='admin_save_page'),
    path('login', LoginUser.as_view(), name='login_page'),
    path('logout', LoginUser.as_view(), name='logout'),
]
