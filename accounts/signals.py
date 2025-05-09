from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order


'''
@receiver(post_save, sender=Order)
def update_turnover(sender, instance, **kwargs):
    if instance.status == 'delivered' and instance.delivery_person:
        delivery_person = instance.delivery_person
        delivery_person.total_turnover += instance.total_price
        delivery_person.save()
'''

'''
@receiver(post_save, sender=Order)
def apply_bonus(sender, instance, created, **kwargs):
    if instance.status == 'delivered' and not instance.bonus_applied:
        instance._check_and_apply_bonus()
        instance.bonus_applied = True
        instance.save(update_fields=['bonus_applied'])
'''

