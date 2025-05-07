from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order

@receiver(post_save, sender=Order)
def update_turnover(sender, instance, **kwargs):
    if instance.status == 'delivered' and instance.delivery_person:
        delivery_person = instance.delivery_person
        delivery_person.total_turnover += instance.total_price
        delivery_person.save()