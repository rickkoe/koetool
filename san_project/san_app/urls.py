from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add_alias, name='add_alias'),
    path('bulk_add_alias/', views.bulk_add_alias, name='bulk_add_alias'),
]


