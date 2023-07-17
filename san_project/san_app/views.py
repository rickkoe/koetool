from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets
from .serializers import SANAliasSerializer
from .models import SANAlias, Fabric, Config
from .forms import ConfigForm
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import IntegrityError
from django.http import JsonResponse  # To send JSON response
from django.views.decorators.csrf import csrf_exempt  # To exempt this view from CSRF protection
import json  # To parse and generate JSON
from collections import defaultdict
# from .scripts import create_port_dict, create_alias_command_dict


def index(request):
    return render(request, 'index.html')


def fabrics_data(request):
    fabrics = Fabric.objects.all()
    data = [{'id': fabric.id, 'name': fabric.name, 'vsan': fabric.vsan} for fabric in fabrics]
    return JsonResponse(data, safe=False)
    

def config(request):
    config_instance, created = Config.objects.get_or_create(pk=1)  # Get or create a single instance
    
    
    if request.method == 'POST':
        form = ConfigForm(request.POST, instance=config_instance)
        if form.is_valid():
            form.save()
            # Handle form submission
    else:
        form = ConfigForm(instance=config_instance)
    context = {'form': form}
    return render(request, 'config.html', context)
    
@csrf_exempt
def aliases(request):
    if request.method == 'POST':
        data = json.loads(request.POST['data'])
            # Update existing records and add new ones
        for row in data:
            print(row)
            for i in row:
                print(row[i])
                if i != 'id' and row[i] == None:
                    print('yup')
                    row[i] = 'False'
            print(row)
            fabric = Fabric.objects.get(id=row['fabric'])
            if row['id']:  # If there's an ID, update the record
                SANAlias.objects.filter(id=row['id']).update(alias_name=row['alias_name'], WWPN=row['WWPN'], use=row['use'], fabric=fabric, create=row['create'], include_in_zoning=row['include_in_zoning'])
            else:  # If there's no ID, create a new record
                san_alias = SANAlias(alias_name=row['alias_name'], WWPN=row['WWPN'], use=row['use'], fabric=fabric, create=row['create'], include_in_zoning=row['include_in_zoning'])
                san_alias.save()
                data[data.index(row)]['id'] = san_alias.id  # Update the data with the newly created alias's ID
        aliases_to_keep = [row['id'] for row in data if row['id']]
        aliases_to_delete = SANAlias.objects.exclude(id__in=aliases_to_keep)
        aliases_to_delete.delete()
        return JsonResponse({'status': 'success'})
    else:
        # For GET requests, we just send all the records to the template
        config = Config.objects.first()
        aliases = SANAlias.objects.values().filter(customer=config.customer)
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
                Fabric.objects.filter(id=row['id']).update(name=row['name'], zoneset_name=row['zoneset_name'], vsan=row['vsan'], exists=row['exists'])
            else:  # If there's no ID, create a new record
                fabric = Fabric(name=row['name'], zoneset_name=row['zoneset_name'], vsan=row['vsan'], exists=row['exists'])
                fabric.save()
                data[data.index(row)]['id'] = fabric.id  # Update the data with the newly created alias's ID
        fabrics_to_keep = [row['id'] for row in data if row['id']]
        fabrics_to_delete = Fabric.objects.exclude(id__in=fabrics_to_keep)
        fabrics_to_delete.delete()
        return JsonResponse({'status': 'success'})
    else:
        # For GET requests, we just send all the records to the template
        fabrics = Fabric.objects.values()
        # Convert boolean values to lowercase false
        for fabric in fabrics:
            if fabric['exists'] is False:
                fabric['exists'] = 'false'

        return render(request, 'fabrics.html', {'fabrics': list(fabrics)})


def create_aliases(request):
    config = Config.objects.first()
    all_aliases = SANAlias.objects.filter(create='True', customer=config.customer)
    print(all_aliases)
    alias_command_dict = defaultdict(list)
    for alias in all_aliases:
        key = alias.fabric.name
        if config.san_vendor == 'CI':
            if config.cisco_alias == 'device-alias':
                if len(alias_command_dict[key]) == 0:
                    alias_command_dict[key].extend(['config t','device-alias database'])
                alias_command_dict[key].append(f'device-alias name {alias.alias_name} pwwn {alias.WWPN}')
            elif config.cisco_alias == 'fcalias':
                alias_command_dict[key].append(f'fcalias name {alias.alias_name} vsan {alias.fabric.vsan} ; member pwwn {alias.WWPN} {alias.use}')
        elif config.san_vendor == 'BR':
            alias_command_dict[key].append(f'alicreate "{alias.alias_name}", "{alias.WWPN}"')
    if config.san_vendor == 'CI' and config.cisco_alias == 'device-alias':
        for key in alias_command_dict:
            alias_command_dict[key].append('device-alias commit')
    alias_command_dict = dict(alias_command_dict)
    # Sort by fabric names
    sorted_dict = dict(sorted(alias_command_dict.items()))
    context = {'alias_command_dict': sorted_dict}
    return render(request, 'create_aliases.html', context)
