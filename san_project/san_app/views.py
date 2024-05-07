from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets
from .serializers import SANAliasSerializer
from .models import Alias, Fabric, Config, ZoneGroup, Storage, Zone, Host, VolumeRange
from .forms import ConfigForm
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json, io, zipfile, datetime
from django.db import IntegrityError, transaction
from django.http import JsonResponse  # To send JSON response
from django.views.decorators.csrf import csrf_exempt  # To exempt this view from CSRF protection
import json  # To parse and generate JSON
from collections import defaultdict
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Prefetch
# from .scripts import create_port_dict, create_alias_command_dict


def index(request):
    return render(request, 'index.html')

def has_member_with_target_use(zone):
    """
    Check if at least one member of the zone has an attribute 'use' equal to 'target'.
    
    Args:
    - zone: Zone instance
    
    Returns:
    - True if at least one member has 'use' equal to 'target', False otherwise
    """
    for member in zone.members.all():
        if member.use == 'target':
            return True
    return False

def merge_dicts(*dicts):
    merged_dict = {}
    for d in dicts:
        for key, value in d.items():
            if key in merged_dict:
                merged_dict[key].extend(value)
            else:
                merged_dict[key] = value
    return merged_dict


def fabrics_data(request):
    config = Config.objects.first()
    fabrics = Fabric.objects.filter(project=config.project)
    data = [{'id': fabric.id, 'name': fabric.name, 'vsan': fabric.vsan, 'exists': fabric.exists} for fabric in fabrics]
    return JsonResponse(data, safe=False)


def storage_data(request):
    config = Config.objects.first()
    storages = Storage.objects.filter(project=config.project)
    data = [{'id': storage.id, 'name': storage.name, 'storage_type': storage.storage_type, 'storage_image': storage.storage_image, 'system_id': storage.system_id, 'location': storage.location} for storage in storages]
    return JsonResponse(data, safe=False)


def alias_data(request):
    config = Config.objects.first()
    aliases = Alias.objects.filter(fabric__project=config.project)
    data = [{'id': alias.id, 'name': alias.name, 'fabric': alias.fabric.name, 'use': alias.use, 'create': alias.create, 'include_in_zoning': alias.include_in_zoning} for alias in aliases]
    return JsonResponse(data, safe=False)   


from django.core.serializers.json import DjangoJSONEncoder
import json

def host_data(request):
    config = Config.objects.first()
    hosts = Host.objects.filter(project=config.project)
    
    # Serialize the ports for each host
    data = [{'id': host.id, 'name': host.name} for host in hosts]
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
    context = {
        'form': form,
        'active_customer': config.project.customer,
        'heading': 'Config',
        'pageview': 'Settings'
        }
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
                    row[field_name] = True
                elif field_value == "false":
                    row[field_name] = False
                elif field_name == 'exists' and field_value == None:
                    row[field_name] = False
            for i in row:
                if i != 'id' and i!= 'storage' and row[i] == None:
                    row[i] = 'False'
            fabric_name = row['fabric']
            try:
                fabric = Fabric.objects.get(name=fabric_name, project=config.project)
            except ObjectDoesNotExist:
                fabric = None  # or handle missing fabric as needed
            if row['storage']:
                storage_name = row['storage']
                try:
                    storage = Storage.objects.get(name=storage_name, project=config.project)
                except ObjectDoesNotExist:
                    storage = None  # or handle missing storage as needed
            if row['host']:
                if row['host'] not in ['null','']:
                    host_name = row['host']
                    try:
                        host = Host.objects.get(name=host_name, project=config.project)
                    except ObjectDoesNotExist:
                        host = Host.objects.create(name=host_name, project=config.project)
            else:
                storage = None
            if row['id']:  # If there's an ID, update the record
                Alias.objects.filter(id=row['id']).update(
                    name=row['name'],
                    wwpn=row['wwpn'],
                    use=row['use'],
                    fabric=fabric,
                    storage=storage,
                    host=host,
                    create=row['create'],
                    include_in_zoning=row['include_in_zoning']
                )
            else:  # If there's no ID, create a new record
                san_alias = Alias(
                    name=row['name'],
                    wwpn=row['wwpn'],
                    use=row['use'],
                    fabric=fabric,
                    storage=storage,
                    host=host,
                    create=row['create'],
                    include_in_zoning=row['include_in_zoning'])
                san_alias.save()
                data[data.index(row)]['id'] = san_alias.id  # Update the data with the newly created alias's ID
        aliases_non_active_customer = Alias.objects.exclude(fabric__project=config.project)
        aliases_to_keep = [row['id'] for row in data if row['id']]
        aliases_to_delete = Alias.objects.exclude(Q(id__in=aliases_to_keep) | Q(id__in=aliases_non_active_customer))
        aliases_to_delete.delete()
        return JsonResponse({'status': 'success'})
    else:
        # For GET requests, we just send all the records to the template

        aliases = Alias.objects.values('id','name','wwpn','use','fabric__name','storage__name','host__name','create','include_in_zoning').filter(fabric__project=config.project)
                # Convert boolean fields to lowercase in each fabric dictionary
        for alias in aliases:
            for field_name, field_value in alias.items():
                if isinstance(field_value, bool):
                    alias[field_name] = str(field_value).lower()
                    # Convert Python None to JSON null
                if field_value is None:
                        alias[field_name] = 'null'
        
        context = {'aliases': list(aliases),
                   'heading': 'Aliases',
                   'pageview': 'Zoning'}  
        return render(request, 'aliases.html', context)


@csrf_exempt
def storage(request):
    config = Config.objects.first()
    if request.method == 'POST':
        data = json.loads(request.POST['data'])
        for row in data:
            if row['id']:  # If there's an ID, update the record
                Storage.objects.filter(id=row['id']).update(
                    project=config.project,
                    name=row['name'],
                    storage_type=row['storage_type'],
                    location=row['location'],
                    machine_type=row['machine_type'],
                    model=row['model'],
                    serial_number=row['serial_number'],
                    firmware_level=row['firmware_level'],
                    storage_image=row['storage_image'],
                    system_id=row['system_id'],
                    primary_ip=row['primary_ip']
                )
            else:  # If there's no ID, create a new record
                storage = Storage(
                    project=config.project,
                    name=row['name'],
                    storage_type=row['storage_type'],
                    location=row['location'],
                    machine_type=row['machine_type'],
                    model=row['model'],
                    serial_number=row['serial_number'],
                    firmware_level=row['firmware_level'],
                    storage_image=row['storage_image'],
                    system_id=row['system_id'],
                    primary_ip=row['primary_ip']
                )
                storage.save()
                data[data.index(row)]['id'] = storage.id  # Update the data with the newly created alias's ID
        storage_non_active_customer = Storage.objects.exclude(project=config.project)
        storage_to_keep = [row['id'] for row in data if row['id']]
        storage_to_delete = Storage.objects.exclude(Q(id__in=storage_to_keep) | Q(id__in=storage_non_active_customer))
        storage_to_delete.delete()
        return JsonResponse({'status': 'success'})
    else:
        storage = Storage.objects.values('id','name','storage_type','location', 'machine_type', 'model', 'serial_number', 'firmware_level', 'storage_image', 'system_id', 'primary_ip').filter(project=config.project)
        for i in storage:
            for field_name, field_value in i.items():
                if isinstance(field_value, bool):
                    i[field_name] = str(field_value).lower()
                    # Convert Python None to JSON null
                if field_value is None:
                        i[field_name] = ''          
        context = {'storage': list(storage),
                   'heading': 'Storage',
                   'pageview': 'Inventory'}  
        return render(request, 'storage.html', context)

@csrf_exempt
def ds_volumegroups(request):
    config = Config.objects.first()
    if request.method == 'POST':
        data = json.loads(request.POST['data'])
        for row in data:
            if row['id']:  # If there's an ID, update the record
                Storage.objects.filter(id=row['id']).update(
                    project=config.project,
                    name=row['name'],
                    storage_type=row['storage_type'],
                    location=row['location'],
                    machine_type=row['machine_type'],
                    model=row['model'],
                    serial_number=row['serial_number'],
                    firmware_level=row['firmware_level'],
                    storage_image=row['storage_image'],
                    system_id=row['system_id'],
                    primary_ip=row['primary_ip']
                )
            else:  # If there's no ID, create a new record
                storage = Storage(
                    project=config.project,
                    name=row['name'],
                    storage_type=row['storage_type'],
                    location=row['location'],
                    machine_type=row['machine_type'],
                    model=row['model'],
                    serial_number=row['serial_number'],
                    firmware_level=row['firmware_level'],
                    storage_image=row['storage_image'],
                    system_id=row['system_id'],
                    primary_ip=row['primary_ip']
                )
                storage.save()
                data[data.index(row)]['id'] = storage.id  # Update the data with the newly created alias's ID
        storage_non_active_customer = Storage.objects.exclude(project=config.project)
        storage_to_keep = [row['id'] for row in data if row['id']]
        storage_to_delete = Storage.objects.exclude(Q(id__in=storage_to_keep) | Q(id__in=storage_non_active_customer))
        storage_to_delete.delete()
        return JsonResponse({'status': 'success'})
    else:
        storage = Storage.objects.values('id','name','storage_type','location', 'machine_type', 'model', 'serial_number', 'firmware_level', 'storage_image', 'system_id', 'primary_ip').filter(project=config.project)
        for i in storage:
            for field_name, field_value in i.items():
                if isinstance(field_value, bool):
                    i[field_name] = str(field_value).lower()
                    # Convert Python None to JSON null
                if field_value is None:
                        i[field_name] = ''          
        context = {'storage': list(storage),
                   'heading': 'Storage',
                   'pageview': 'Inventory'}  
        return render(request, 'storage.html', context)


@csrf_exempt
def ds_volume_ranges(request):
    config = Config.objects.first()
    if request.method == 'POST':
        data = json.loads(request.POST['data'])
        print(data)
        for row in data:
            for field_name, field_value in row.items():
                if field_value == "true":
                    row[field_name] = True
                elif field_value == "false":
                    row[field_name] = False
                elif field_name == 'exists' and field_value == None:
                    row[field_name] = False
            for i in row:
                if i != 'id' and row[i] == None:
                    row[i] = 'False'
                if row['id']:  # If there's an ID, update the record
                    volume_range = VolumeRange.objects.get(id=row['id'])
                    field_list = ['site',
                                'lpar',
                                'use',
                                # 'source_ds8k',
                                'source_pool',
                                'source_start',
                                'source_end',
                                # 'target_ds8k',
                                'target_start',
                                'target_end',
                                'create']
                    for field in field_list:
                        setattr(volume_range, field, row[field])
                    volume_range.save()
                else:  # If there's no ID, create a new record
                    volume_range = VolumeRange()
                    setattr(volume_range, 'project', config.project)
                    field_list = ['site',
                                'lpar',
                                'use',
                                # 'source_ds8k',
                                'source_pool',
                                'source_start',
                                'source_end',
                                # 'target_ds8k',
                                'target_start',
                                'target_end',
                                'create']
                    for field in field_list:
                        setattr(volume_range, field, row[field])
                    volume_range.save()

        return JsonResponse({'status': 'success'})
    else:
        config = Config.objects.first()
        volume_ranges = VolumeRange.objects.values('id','site','lpar','use','source_ds8k__name','source_pool','source_start','source_end','target_ds8k__name','target_start','target_end','create').filter(project=config.project)

        # Convert boolean fields to lowercase in each fabric dictionary
        for volume_range in volume_ranges:
            for field_name, field_value in volume_range.items():
                if isinstance(field_value, bool):
                    volume_range[field_name] = str(field_value).lower()
        context = {'volume_ranges': list(volume_ranges),
                'heading': 'Volume Ranges',
                'pageview': 'DS8000'}  

        return render(request, 'ds-volume-ranges.html', context)


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
                    row[field_name] = True
                elif field_value == "false":
                    row[field_name] = False
                elif field_name == 'exists' and field_value == None:
                    row[field_name] = False
                if field_name == 'vsan' and field_value == None:
                    row[field_name] = 1
            if row and row['name']:
                existing_fabric = Fabric.objects.filter(project=config.project, name=row['name']).exclude(id=row.get('id'))
                if existing_fabric.exists():
                    errors.append(f"Fabric name '{row['name']}' already exists for the customer.")

        if errors:
            return JsonResponse({'status': 'error', 'errors': errors})
        
        for row in data:
            if row and row['id']:  # If there's an ID, update the record
                Fabric.objects.filter(id=row['id']).update(project=config.project, name=row['name'], zoneset_name=row['zoneset_name'], vsan=row['vsan'], exists=row['exists'])
            else:  # If there's no ID, create a new record
                fabric = Fabric(project=config.project, name=row['name'], zoneset_name=row['zoneset_name'], vsan=row['vsan'], exists=row['exists'])
                fabric.save()
                data[data.index(row)]['id'] = fabric.id  # Update the data with the newly created alias's ID
        fabrics_non_active_customer = Fabric.objects.exclude(project=config.project)
        fabrics_to_keep = [row['id'] for row in data if row['id']]
        fabrics_to_delete = Fabric.objects.exclude(Q(id__in=fabrics_to_keep) | Q(id__in=fabrics_non_active_customer))
        fabrics_to_delete.delete()
        return JsonResponse({'status': 'success'})
    else:
        config = Config.objects.first()
        fabrics = Fabric.objects.values().filter(project=config.project)

        # Convert boolean fields to lowercase in each fabric dictionary
        for fabric in fabrics:
            for field_name, field_value in fabric.items():
                if isinstance(field_value, bool):
                    fabric[field_name] = str(field_value).lower()
        context = {'fabrics': list(fabrics),
                   'heading': 'Fabrics',
                   'pageview': 'Inventory'}  

        return render(request, 'fabrics.html', context)


@csrf_exempt
def zone_groups(request):
    config = Config.objects.first()
    if request.method == 'POST':
        data = json.loads(request.POST['data'])
            # Update existing records and add new ones
        for row in data:
            for field_name, field_value in row.items():
                if field_value == "true":
                    row[field_name] = True
                elif field_value == "false":
                    row[field_name] = False
                elif field_name == 'exists' and field_value == None:
                    row[field_name] = False
            for i in row:
                if i != 'id' and row[i] == None:
                    row[i] = 'False'
            fabric = Fabric.objects.get(name=row['fabric'], project=config.project)
            storage = Storage.objects.get(name=row['storage'], project=config.project)
            if row['id']:  # If there's an ID, update the record
                ZoneGroup.objects.filter(id=row['id']).update(name=row['name'], fabric=fabric, storage=storage, zone_type=row['zone_type'], create=row['create'], exists=row['exists'])
            else:  # If there's no ID, create a new record
                zone_group = ZoneGroup(name=row['name'], fabric=fabric, storage=storage, zone_type=row['zone_type'], create=row['create'], exists=row['exists'])
                zone_group.save()
                data[data.index(row)]['id'] = zone_group.id  # Update the data with the newly created alias's ID
        zones_non_active_customer = ZoneGroup.objects.exclude(fabric__project=config.project)
        zones_to_keep = [row['id'] for row in data if row['id']]
        zones_to_delete = ZoneGroup.objects.exclude(Q(id__in=zones_to_keep) | Q(id__in=zones_non_active_customer))
        zones_to_delete.delete()
        return JsonResponse({'status': 'success'})
    else:
        # For GET requests, we just send all the records to the template

        zone_groups = ZoneGroup.objects.values('id','name','fabric__name', 'storage__name', 'zone_type','create','exists').filter(fabric__project=config.project)
                # Convert boolean fields to lowercase in each fabric dictionary
        for zone_group in zone_groups:
            for field_name, field_value in zone_group.items():
                if isinstance(field_value, bool):
                    zone_group[field_name] = str(field_value).lower()
        return render(request, 'zone-groups.html', {'zone_groups': list(zone_groups)})

@csrf_exempt
def zones(request):
    config = Config.objects.first()
    if request.method == 'POST':
        data = json.loads(request.POST['data'])
        max_uses = json.loads(request.POST['max_uses'])
        config.alias_max_zones = max_uses
        config.save()

            # Update existing records and add new ones
        for row in data:
            for field_name, field_value in row.items():
                if field_value == "true":
                    row[field_name] = True
                elif field_value == "false":
                    row[field_name] = False
                elif field_name == 'exists' and field_value == None:
                    row[field_name] = False
            for i in row:
                if i != 'id' and row[i] == None:
                    row[i] = 'False'
            fabric = Fabric.objects.get(name=row['fabric'], project=config.project)
            if row['id']:  # If there's an ID, update the record
                zone = Zone.objects.get(id=row['id'])
                zone.members.clear()
                zone.name = row['name']
                zone.fabric = fabric
                zone.zone_type = row['zone_type']
                zone.create = row['create']
                zone.exists = row['exists']
                zone.save()
                members = row['members']
                if members:
                    for member in members:
                        if member:
                            zone.members.add(Alias.objects.get(name=member))  # Adjusted to use f-string for dynamic member access
                    zone.save()

            else:  # If there's no ID, create a new record
                zone = Zone(
                    name=row['name'],
                    fabric=fabric,
                    zone_type=row['zone_type'],
                    create=row['create'],
                    exists=row['exists']
                    )
                zone.save()
                members = row['members']
                if members:
                    for member in members:
                        if member:
                            zone.members.add(Alias.objects.get(name=member))  # Adjusted to use f-string for dynamic member access
                    zone.save()
                data[data.index(row)]['id'] = zone.id  # Update the data with the newly created alias's ID
        zones_non_active_customer = Zone.objects.exclude(fabric__project=config.project)
        zones_to_keep = [row['id'] for row in data if row['id']]
        zones_to_delete = Zone.objects.exclude(Q(id__in=zones_to_keep) | Q(id__in=zones_non_active_customer))
        zones_to_delete.delete()
        return JsonResponse({'status': 'success'})
    else:
        # For GET requests, we just send all the records to the template

        zones = Zone.objects.select_related('fabric').prefetch_related('members').filter(fabric__project=config.project).order_by('id')
                # Convert boolean fields to lowercase in each fabric dictionary
    # Create a list to store dictionary representations of Zone objects
    zone_data = []

    # Iterate over each Zone object in the queryset
    for zone in zones:
        # Create a dictionary to represent the Zone object
        zone_dict = {
            'id': zone.id,
            'name': zone.name,
            'fabric__name': zone.fabric.name,
            'create': str(zone.create).lower(),
            'exists': str(zone.exists).lower(),
            'zone_type': zone.zone_type,
            'members': [member.name for member in zone.members.all()]  # Assuming members is a related field
        }
        
        # Append the dictionary to the zone_data list
        zone_data.append(zone_dict)
    # Pass the list of dictionaries to the template
    context = {'zones': zone_data,
                'maxUses': config.alias_max_zones,
                'heading': 'Zones',
                'pageview': 'Zoning'}      
    return render(request, 'zones.html', context)

    

def create_aliases(request):
    config = Config.objects.first()
    all_aliases = Alias.objects.filter(create='True', fabric__project=config.project)
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
    context = {
        'alias_command_dict': sorted_dict,
        'heading': 'Alias Commands',
        'pageview': 'Aliases'
               }
    return render(request, 'create_aliases.html', context)


def create_hosts(request):
    config = Config.objects.first()
    all_hosts = Alias.objects.filter(create='True', fabric__project=config.project)
    host_command_dict = defaultdict(list)
    for host in all_hosts:
        key = host.fabric.name
        if config.san_vendor == 'CI':
            if config.cisco_host == 'device-host':
                if len(host_command_dict[key]) == 0:
                    host_command_dict[key].extend(['config t','device-host database'])
                host_command_dict[key].append(f'device-host name {host.name} pwwn {host.wwpn}')
            elif config.cisco_host == 'fchost':
                host_command_dict[key].append(f'fchost name {host.name} vsan {host.fabric.vsan} ; member pwwn {host.wwpn} {host.use}')
        elif config.san_vendor == 'BR':
            host_command_dict[key].append(f'alicreate "{host.name}", "{host.wwpn}"')
    if config.san_vendor == 'CI' and config.cisco_host == 'device-host':
        for key in host_command_dict:
            host_command_dict[key].append('device-host commit')
    host_command_dict = dict(host_command_dict)
    # Sort by fabric names
    sorted_dict = dict(sorted(host_command_dict.items()))
    context = {
        'host_command_dict': sorted_dict,
        'heading': 'Alias Commands',
        'pageview': 'Aliases'
               }
    return render(request, 'create_hosts.html', context)

# Create Alias Commands
def create_zone_command_dict():
    config = Config.objects.first()
    all_aliases = Alias.objects.filter(create='True', fabric__project=config.project)
    alias_command_dict = defaultdict(list)
    zone_command_dict = defaultdict(list)
    zoneset_command_dict = defaultdict(list)
    for alias in all_aliases:
        key = alias.fabric.name
        if key not in alias_command_dict:
            alias_command_dict[key].append(f'### ALIAS COMMANDS FOR {key.upper()}')
        if config.san_vendor == 'CI':
            if config.cisco_alias == 'device-alias':
                if len(alias_command_dict[key]) == 1:
                    alias_command_dict[key].extend(['config t','device-alias database'])
                alias_command_dict[key].append(f'device-alias name {alias.name} pwwn {alias.wwpn}')
            elif config.cisco_alias == 'fcalias':
                if len(alias_command_dict[key]) == 1:
                    alias_command_dict[key].append('config t')
                alias_command_dict[key].append(f'fcalias name {alias.name} vsan {alias.fabric.vsan} ; member pwwn {alias.wwpn} {alias.use}')
        elif config.san_vendor == 'BR':
            alias_command_dict[key].append(f'alicreate "{alias.name}", "{alias.wwpn}"')
    if config.san_vendor == 'CI' and config.cisco_alias == 'device-alias':
        for key in alias_command_dict:
            alias_command_dict[key].append('device-alias commit')
    # Create Zone Commands
    alias_type = config.cisco_alias
    all_zones = Zone.objects.select_related('fabric').prefetch_related('members').filter(create='True', fabric__project=config.project).order_by('id')
    firstpass = False # Set trigger for Cisco config t command
    for zone in all_zones:
        zone_members = zone.members.all()
        zone_member_list = []
        for zone_member in zone_members:
            zone_member_list.append(zone_member.name)
        key = zone.fabric.name
        if key not in zone_command_dict:
            zone_command_dict[key].extend(['',f'### ZONE COMMANDS FOR {key.upper()} '])
        if key not in zoneset_command_dict:
            zoneset_command_dict[key].extend(['',f'### ZONESET COMMANDS FOR {key.upper()} '])
        if config.san_vendor == 'CI':
            if firstpass == False:
                zone_command_dict[key].append('config t')
                firstpass = True
            if len(zoneset_command_dict[key]) == 2:
                zoneset_command_dict[key].append(f'zoneset name {zone.fabric.zoneset_name} vsan {zone.fabric.vsan}')
            zone_command_dict[key].append(f'zone name {zone.name} vsan {zone.fabric.vsan}')
            if zone.exists == False:
                zoneset_command_dict[key].append(f'member {zone.name}')
            for zone_member in zone_members:
                if config.cisco_alias == 'fcalias':  
                    zone_command_dict[key].append(f'member {alias_type} {zone_member.name}')
                elif config.cisco_alias == 'device-alias' and zone.zone_type == 'smart_peer':
                    zone_command_dict[key].append(f'member {alias_type} {zone_member.name} {zone_member.use}')
                elif config.cisco_alias == 'device-alias' and zone.zone_type == 'standard':
                    zone_command_dict[key].append(f'member {alias_type} {zone_member.name}')
                elif config.cisco_alias == 'wwpn':
                    if zone.zone_type == 'smart_peer':
                        zone_command_dict[key].append(f'member pwwn {zone_member.wwpn} {zone_member.use}')
                    elif zone.zone_type == 'standard':
                        zone_command_dict[key].append(f'member pwwn {zone_member.wwpn}')
        if config.san_vendor == 'BR':
            if zone.zone_type == 'standard':
                zone_member_list = ';'.join(zone_member_list)
                if zone.exists == True:
                    zone_command_dict[key].append(f'zoneadd "{zone.name}", "{zone_member_list}"')
                elif zone.exists == False:
                    zone_command_dict[key].append(f'zonecreate "{zone.name}", "{zone_member_list}"')
            elif zone.zone_type == 'smart_peer':
                initiators = ';'.join([alias.name for alias in zone_members if alias.use == 'init'])
                targets = ';'.join([alias.name for alias in zone_members if alias.use == 'target'])
                if zone.exists == True:
                    zone_command_dict[key].append(f'zoneadd --peerzone "{zone.name}" -principal "{targets}" -members "{initiators}"')
                elif zone.exists == False:
                    zone_command_dict[key].append(f'zonecreate --peerzone "{zone.name}" -principal "{targets}" -members "{initiators}"')
            if len(zoneset_command_dict[key]) == 2 and zone.fabric.exists == False and zone.exists == False:
                zoneset_command_dict[key].append(f'cfgcreate "{zone.fabric.zoneset_name}", "{zone.name}"')
            elif zone.exists == False:
                zoneset_command_dict[key].append(f'cfgadd "{zone.fabric.zoneset_name}", "{zone.name}"')
            else:
                print(f'Zone {zone.name} not added to a config:   Fabric: {zone.fabric.exists} Zone: {zone.exists}')

    
    for key in zoneset_command_dict:
        fabric = Fabric.objects.get(name=key, project=config.project)
        if config.san_vendor == 'CI':
            zoneset_command_dict[key].append(f'zoneset activate name {fabric.zoneset_name} vsan {fabric.vsan}')
            if config.cisco_zoning_mode == 'enhanced':
                zoneset_command_dict[key].append(f'zone commit vsan {fabric.vsan}')
        elif config.san_vendor == 'BR':
            zoneset_command_dict[key].append(f'cfgenable "{fabric.zoneset_name}"')
    command_dict = merge_dicts(alias_command_dict, zone_command_dict, zoneset_command_dict)
    command_dict = dict(command_dict)
    # Sort by fabric names
    sorted_command_dict = dict(sorted(command_dict.items()))
    return sorted_command_dict

def create_zones(request):
    zone_command_dict = create_zone_command_dict()
    context = {
        'zone_command_dict': zone_command_dict,
        'heading': 'Zone Commands',
        'pageview': 'Zones'
        }
    return render(request, 'create_zones.html', context)

# Create Alias Commands
def download_commands_zip(request):
    config = Config.objects.first()
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    download_filename = f'{config.project.customer.name} {config.zoning_job_name} Zoning Commands {timestamp}.zip'
    zone_command_dict = create_zone_command_dict()
    # Create a zip file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a') as zip_file:
        for filename, content in zone_command_dict.items():
            # Write each file to the zip file
            with zip_file.open(f'{filename} {config.zoning_job_name} {timestamp}.txt', 'w') as file:
                for line in content:
                    file.write((line + '\n').encode())

    # Create the HTTP response
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{download_filename}"'

    return response


@csrf_exempt
def hosts(request):
    config = Config.objects.first()
    if request.method == 'POST':
        data = json.loads(request.POST['data'])

        # Update existing records and add new ones
        for row in data:            
            # Ensure that fields with None values are set to 'False' string

            if row['id']:  # If there's an ID, update the record
                Host.objects.filter(id=row['id']).update(
                    name=row['name']
                )
            elif row['name'] not in [None,'']:
                print(row['name'])
                host = Host.objects.create(
                    name=row['name'],
                    project=config.project
                )
                row['id'] = host.id  # Update the data with the newly created host's ID


        # Delete hosts that are not in the received data
        hosts_to_keep = [row['id'] for row in data if row['id']]
        hosts_to_delete = Host.objects.exclude(id__in=hosts_to_keep)
        hosts_to_delete.delete()

        return JsonResponse({'status': 'success'})
    else:
        # For GET requests, retrieve all host records with associated aliases
        hosts = Host.objects.filter(project=config.project).prefetch_related(
            Prefetch('alias_host', queryset=Alias.objects.select_related('storage').order_by('name'))
        )

        # Extract host data from the prefetch_related queryset
        host_data = []
        for host in hosts:
            host_dict = {
                'id': host.id,
                'name': host.name,
                'wwpns': []
            }
            # Extract alias data for the host
            for alias in host.alias_host.all():
                host_dict['wwpns'].append(alias.wwpn)
            
            host_data.append(host_dict)

        # Now, you can use the `host_data` list in your context
        context = {
            'hosts': host_data,
            'heading': 'Hosts',
            'pageview': 'DS8000'
        }
        return render(request, 'hosts.html', context)
