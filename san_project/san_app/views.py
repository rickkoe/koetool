from django.shortcuts import render, redirect, get_object_or_404
from .forms import SANAliasForm, BulkUploadForm
from rest_framework import viewsets
from .serializers import SANAliasSerializer
from .models import SANAlias, Fabric
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import IntegrityError
from django.http import JsonResponse  # To send JSON response
from django.views.decorators.csrf import csrf_exempt  # To exempt this view from CSRF protection
import json  # To parse and generate JSON


def index(request):
    return render(request, 'index.html')


def fabrics_data(request):
    fabrics = Fabric.objects.all()
    data = [{'id': fabric.id, 'name': fabric.name, 'vsan': fabric.vsan} for fabric in fabrics]
    return JsonResponse(data, safe=False)
    

@csrf_exempt
def aliases(request):
    if request.method == 'POST':
        data = json.loads(request.POST['data'])
        # Update existing records and add new ones
        for row in data:
            fabric = Fabric.objects.get(id=row['fabric'])
            if row['id']:  # If there's an ID, update the record
                SANAlias.objects.filter(id=row['id']).update(alias_name=row['alias_name'], WWPN=row['WWPN'], use=row['use'], fabric=fabric)
            else:  # If there's no ID, create a new record
                san_alias = SANAlias(alias_name=row['alias_name'], WWPN=row['WWPN'], use=row['use'], fabric=fabric)
                san_alias.save()
                data[data.index(row)]['id'] = san_alias.id  # Update the data with the newly created alias's ID
        aliases_to_keep = [row['id'] for row in data if row['id']]
        aliases_to_delete = SANAlias.objects.exclude(id__in=aliases_to_keep)
        aliases_to_delete.delete()
        return JsonResponse({'status': 'success'})
    else:
        # For GET requests, we just send all the records to the template
        aliases = SANAlias.objects.values()
        return render(request, 'aliases.html', {'aliases': list(aliases)})
    

@csrf_exempt
def fabrics(request):
    if request.method == 'POST':
        data = json.loads(request.POST['data'])
        # print(data)
        # Update existing records and add new ones
        for row in data:
            if row and row['id']:  # If there's an ID, update the record
                # print(row)
                Fabric.objects.filter(id=row['id']).update(name=row['name'], san_vendor=row['san_vendor'], zoneset_name=row['zoneset_name'], vsan=row['vsan'])
            else:  # If there's no ID, create a new record
                fabric = Fabric(name=row['name'], san_vendor=row['san_vendor'], zoneset_name=row['zoneset_name'], vsan=row['vsan'])
                fabric.save()
                data[data.index(row)]['id'] = fabric.id  # Update the data with the newly created alias's ID
        fabrics_to_keep = [row['id'] for row in data if row['id']]
        fabrics_to_delete = Fabric.objects.exclude(id__in=fabrics_to_keep)
        fabrics_to_delete.delete()
        return JsonResponse({'status': 'success'})
    else:
        # For GET requests, we just send all the records to the template
        fabrics = Fabric.objects.values()
        return render(request, 'fabrics.html', {'fabrics': list(fabrics)})