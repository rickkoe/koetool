from django.shortcuts import render, redirect
from .forms import SANAliasForm, BulkUploadForm
from rest_framework import viewsets
from .serializers import SANAliasSerializer
from .models import SANAlias
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import IntegrityError

def index(request):
    aliases = SANAlias.objects.all()
    return render(request, 'index.html', {'aliases': aliases})


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