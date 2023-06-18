from django.shortcuts import render, redirect
from .forms import SANAliasForm, BulkUploadForm
from rest_framework import viewsets
from .serializers import SANAliasSerializer
from .models import SANAlias
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import IntegrityError
from django.http import JsonResponse  # To send JSON response
from django.views.decorators.csrf import csrf_exempt  # To exempt this view from CSRF protection
import json  # To parse and generate JSON

import logging

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'index.html')

@csrf_exempt
def aliases(request):
    if request.method == 'POST':
        data = json.loads(request.POST['data'])
        
        logger.debug(f"Received data: {data}")  # Add this line

        # Update existing records and add new ones
        for row in data:
            if row['id']:  # If there's an ID, update the record
                SANAlias.objects.filter(id=row['id']).update(alias_name=row['alias_name'], WWPN=row['WWPN'], use=row['use'])
            else:  # If there's no ID, create a new record
                san_alias = SANAlias(alias_name=row['alias_name'], WWPN=row['WWPN'], use=row['use'])
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


def add_alias(request):
    if request.method == 'POST':
        form = SANAliasForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = SANAliasForm()
    return render(request, 'add_alias.html', {'form': form})


@csrf_exempt
def bulk_add_alias(request):
    if request.method == 'POST':
        data = json.loads(request.POST.get('data'))
        for row in data:
            if len(row) == 3 and all(row):
                try:
                    alias = SANAlias(alias_name=row[0], WWPN=row[1], use=row[2])
                    alias.save()
                except IntegrityError:
                     # Handle the error here. For example, you might want to return an error message
                    return JsonResponse({"success": False, "error": "Duplicate entry"})
        return JsonResponse({"success": True})
    else:
        form = BulkUploadForm()

    return render(request, 'bulk_add_alias.html', {'form': form})



class SANAliasViewSet(viewsets.ModelViewSet):
    queryset = SANAlias.objects.all()
    serializer_class = SANAliasSerializer