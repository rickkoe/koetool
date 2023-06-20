from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('aliases/', views.aliases, name='aliases'),
    path('add/', views.add_alias, name='add_alias'),
    path('bulk_add_alias/', views.bulk_add_alias, name='bulk_add_alias'),
    path('fabrics/', views.fabrics_data_view, name='fabrics_data'),
]


