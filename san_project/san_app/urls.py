from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('aliases/', views.aliases, name='aliases'),
    path('fabrics_data/', views.fabrics_data, name='fabrics_data'),
    path('fabrics/', views.fabrics, name='fabrics'),
]


