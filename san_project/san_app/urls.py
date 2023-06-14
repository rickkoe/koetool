from django.urls import path
from .views import index, add_alias

urlpatterns = [
    path('', index, name='index'),
    path('add/', add_alias, name='add_alias'),
]
