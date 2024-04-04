from .models import Config

def active_customer(request):
    # Assuming you have a foreign key relationship from Config to Customer
    config = Config.objects.select_related('project').first()
    return {'active_project': config.project if config else None}
