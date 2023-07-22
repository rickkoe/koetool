from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets
from .serializers import SANAliasSerializer
from .models import Alias, Fabric, Config, Zone
from .forms import ConfigForm
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import IntegrityError
from django.http import JsonResponse  # To send JSON response
from django.views.decorators.csrf import csrf_exempt  # To exempt this view from CSRF protection
import json  # To parse and generate JSON
from collections import defaultdict
from django.db.models import Q
# from .scripts import create_port_dict, create_alias_command_dict


def index(request):
    return render(request, 'index.html')


def fabrics_data(request):
    config = Config.objects.first()
    fabrics = Fabric.objects.filter(customer=config.customer)
    data = [{'id': fabric.id, 'name': fabric.name, 'vsan': fabric.vsan, 'exists': fabric.exists} for fabric in fabrics]
    return JsonResponse(data, safe=False)
    

def config(request):
    config_instance, created = Config.objects.get_or_create(pk=1)  # Get or create a single instance
    
    if request.method == 'POST':
        form = ConfigForm(request.POST, instance=config_instance)
        if form.is_valid():
            form.save()
            return redirect('config')  # Redirect back to the config page
    else:
        form = ConfigForm(instance=config_instance)
    config = Config.objects.first()
    context = {'form': form, 'active_customer': config.customer}
    return render(request, 'config.html', context)
    
@csrf_exempt
def aliases(request):
    config = Config.objects.first()
    if request.method == 'POST':
        data = json.loads(request.POST['data'])
            # Update existing records and add new ones
        for row in data:
            for field_name, field_value in row.items():
                if field_value == "true":
                    print(field_value)
                    row[field_name] = True
                elif field_value == "false":
                    row[field_name] = False
                elif field_name == 'exists' and field_value == None:
                    row[field_name] = False
            for i in row:
                if i != 'id' and row[i] == None:
                    row[i] = 'False'
            print(row)
            fabric = Fabric.objects.get(name=row['fabric'], customer=config.customer)
            print(f'FABRIC: {fabric.name}')
            if row['id']:  # If there's an ID, update the record
                Alias.objects.filter(id=row['id']).update(customer=config.customer, name=row['name'], wwpn=row['wwpn'], use=row['use'], fabric=fabric, create=row['create'], include_in_zoning=row['include_in_zoning'])
            else:  # If there's no ID, create a new record
                san_alias = Alias(customer=config.customer,name=row['name'], wwpn=row['wwpn'], use=row['use'], fabric=fabric, create=row['create'], include_in_zoning=row['include_in_zoning'])
                san_alias.save()
                data[data.index(row)]['id'] = san_alias.id  # Update the data with the newly created alias's ID
        aliases_non_active_customer = Alias.objects.exclude(customer=config.customer)
        aliases_to_keep = [row['id'] for row in data if row['id']]
        aliases_to_delete = Alias.objects.exclude(Q(id__in=aliases_to_keep) | Q(id__in=aliases_non_active_customer))
        aliases_to_delete.delete()
        return JsonResponse({'status': 'success'})
    else:
        # For GET requests, we just send all the records to the template

        aliases = Alias.objects.values('id','name','wwpn','use','fabric__name','create','include_in_zoning').filter(customer=config.customer)
                # Convert boolean fields to lowercase in each fabric dictionary
        for alias in aliases:
            for field_name, field_value in alias.items():
                if isinstance(field_value, bool):
                    alias[field_name] = str(field_value).lower()
        return render(request, 'aliases.html', {'aliases': list(aliases)})
    

@csrf_exempt
def fabrics(request):
    if request.method == 'POST':
        config = Config.objects.first()
        data = json.loads(request.POST['data'])

        # Validation and error handling
        errors = []
        for row in data:
            for field_name, field_value in row.items():
                if field_value == "true":
                    print(field_value)
                    row[field_name] = True
                elif field_value == "false":
                    row[field_name] = False
                elif field_name == 'exists' and field_value == None:
                    row[field_name] = False
                if field_name == 'vsan' and field_value == None:
                    row[field_name] = 1
            if row and row['name']:
                existing_fabric = Fabric.objects.filter(customer=config.customer, name=row['name']).exclude(id=row.get('id'))
                if existing_fabric.exists():
                    errors.append(f"Fabric name '{row['name']}' already exists for the customer.")

        if errors:
            return JsonResponse({'status': 'error', 'errors': errors})
        
        for row in data:
            if row and row['id']:  # If there's an ID, update the record
                Fabric.objects.filter(id=row['id']).update(customer=config.customer, name=row['name'], zoneset_name=row['zoneset_name'], vsan=row['vsan'], exists=row['exists'])
            else:  # If there's no ID, create a new record
                fabric = Fabric(customer=config.customer, name=row['name'], zoneset_name=row['zoneset_name'], vsan=row['vsan'], exists=row['exists'])
                fabric.save()
                data[data.index(row)]['id'] = fabric.id  # Update the data with the newly created alias's ID
        fabrics_non_active_customer = Fabric.objects.exclude(customer=config.customer)
        fabrics_to_keep = [row['id'] for row in data if row['id']]
        fabrics_to_delete = Fabric.objects.exclude(Q(id__in=fabrics_to_keep) | Q(id__in=fabrics_non_active_customer))
        fabrics_to_delete.delete()
        return JsonResponse({'status': 'success'})
    else:
        config = Config.objects.first()
        fabrics = Fabric.objects.values().filter(customer=config.customer)

        # Convert boolean fields to lowercase in each fabric dictionary
        for fabric in fabrics:
            for field_name, field_value in fabric.items():
                if isinstance(field_value, bool):
                    fabric[field_name] = str(field_value).lower()
        print(list(fabrics))
        return render(request, 'fabrics.html', {'fabrics': list(fabrics)})


@csrf_exempt
def zones(request):
    config = Config.objects.first()
    if request.method == 'POST':
        data = json.loads(request.POST['data'])
            # Update existing records and add new ones
        for row in data:
            for field_name, field_value in row.items():
                if field_value == "true":
                    print(field_value)
                    row[field_name] = True
                elif field_value == "false":
                    row[field_name] = False
                elif field_name == 'exists' and field_value == None:
                    row[field_name] = False
            for i in row:
                if i != 'id' and row[i] == None:
                    row[i] = 'False'
            print(row)
            fabric = Fabric.objects.get(name=row['fabric'], customer=config.customer)
            print(f'FABRIC: {fabric.name}')
            if row['id']:  # If there's an ID, update the record
                Zone.objects.filter(id=row['id']).update(name=row['name'], fabric=fabric, zone_type=row['zone_type'], create=row['create'], exists=row['exists'])
            else:  # If there's no ID, create a new record
                zone = Zone(name=row['name'], fabric=fabric, zone_type=row['zone_type'], create=row['create'], exists=row['exists'])
                zone.save()
                data[data.index(row)]['id'] = zone.id  # Update the data with the newly created alias's ID
        zones_non_active_customer = Zone.objects.exclude(fabric__customer=config.customer)
        zones_to_keep = [row['id'] for row in data if row['id']]
        zones_to_delete = Zone.objects.exclude(Q(id__in=zones_to_keep) | Q(id__in=zones_non_active_customer))
        zones_to_delete.delete()
        return JsonResponse({'status': 'success'})
    else:
        # For GET requests, we just send all the records to the template

        zones = Zone.objects.values('id','name','fabric__name','zone_type','create','exists').filter(fabric__customer=config.customer)
                # Convert boolean fields to lowercase in each fabric dictionary
        for zone in zones:
            for field_name, field_value in zone.items():
                if isinstance(field_value, bool):
                    zone[field_name] = str(field_value).lower()
                print(field_name, field_value)
        return render(request, 'zones.html', {'zones': list(zones)})

def create_aliases(request):
    config = Config.objects.first()
    all_aliases = Alias.objects.filter(create='True', customer=config.customer)
    print(all_aliases)
    alias_command_dict = defaultdict(list)
    for alias in all_aliases:
        key = alias.fabric.name
        if config.san_vendor == 'CI':
            if config.cisco_alias == 'device-alias':
                if len(alias_command_dict[key]) == 0:
                    alias_command_dict[key].extend(['config t','device-alias database'])
                alias_command_dict[key].append(f'device-alias name {alias.name} pwwn {alias.wwpn}')
            elif config.cisco_alias == 'fcalias':
                alias_command_dict[key].append(f'fcalias name {alias.name} vsan {alias.fabric.vsan} ; member pwwn {alias.wwpn} {alias.use}')
        elif config.san_vendor == 'BR':
            alias_command_dict[key].append(f'alicreate "{alias.name}", "{alias.wwpn}"')
    if config.san_vendor == 'CI' and config.cisco_alias == 'device-alias':
        for key in alias_command_dict:
            alias_command_dict[key].append('device-alias commit')
    alias_command_dict = dict(alias_command_dict)
    # Sort by fabric names
    sorted_dict = dict(sorted(alias_command_dict.items()))
    context = {'alias_command_dict': sorted_dict}
    return render(request, 'create_aliases.html', context)
