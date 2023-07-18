from .models import Config

def active_customer(request):
    # Assuming you have a foreign key relationship from Config to Customer
    config = Config.objects.select_related('customer').first()
    return {'active_customer': config.customer if config else None}
