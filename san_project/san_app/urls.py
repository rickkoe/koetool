from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('config/', views.config, name='config'),
    path('aliases/', views.aliases, name='aliases'),
    path('hosts/', views.hosts, name='hosts'),
    path('fabrics_data/', views.fabrics_data, name='fabrics_data'),
    path('storage_data/', views.storage_data, name='storage_data'),   
    path('alias_data/', views.alias_data, name='alias_data'),
    path('host_data/', views.host_data, name='host_data'),
    path('fabrics/', views.fabrics, name='fabrics'),
    path('zone-groups/', views.zone_groups, name='zone_groups'),
    path('create-aliases/', views.create_aliases, name='create_aliases'),
    path('create-hosts/', views.create_hosts, name='create_hosts'),
    path('create-zones/', views.create_zones, name='create_zones'),
    path('storage/', views.storage, name='storage'),
    path('zones/', views.zones, name='zones'),
    path('download-commands-zip/', views.download_commands_zip, name='download_commands_zip'),
]