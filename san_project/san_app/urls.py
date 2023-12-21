from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('config/', views.config, name='config'),
    path('aliases/', views.aliases, name='aliases'),
    path('fabrics_data/', views.fabrics_data, name='fabrics_data'),
    path('fabrics/', views.fabrics, name='fabrics'),
    path('zone-groups/', views.zone_groups, name='zone_groups'),
    path('create-aliases/', views.create_aliases, name='create_aliases'),
    path('storage/', views.storage, name='storage'),
    path('zones/', views.zones, name='zones'),
]