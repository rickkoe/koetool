from django.shortcuts import render, redirect
from .forms import SANAliasForm
from rest_framework import viewsets
from .serializers import SANAliasSerializer
from .models import SANAlias

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


class SANAliasViewSet(viewsets.ModelViewSet):
    queryset = SANAlias.objects.all()
    serializer_class = SANAliasSerializer