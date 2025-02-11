from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import BaseSupply, DetailSupply, CostEstimation

@receiver(pre_save, sender=DetailSupply)
def sync_detail_supply_on_create(sender, instance, **kwargs):
    """ Sync data from BaseSupply when creating or updating a DetailSupply record """
    if instance.base_supply:
        instance.material_type = instance.base_supply.material_type
        instance.supply_number = instance.base_supply.supply_number
        instance.supply_name = instance.base_supply.supply_name
        instance.unit = instance.base_supply.unit
        instance.image = instance.base_supply.image

@receiver(post_save, sender=BaseSupply)
def update_detail_supply_on_base_change(sender, instance, **kwargs):
    """ Update all related DetailSupply records when BaseSupply changes """
    DetailSupply.objects.filter(base_supply=instance).update(
        material_type=instance.material_type,
        supply_number=instance.supply_number,
        supply_name=instance.supply_name,
        unit=instance.unit,
        image=instance.image
    )

@receiver(pre_save, sender=CostEstimation)
def sync_cost_estimation_on_create(sender, instance, **kwargs):
    """ Sync data from BaseSupply when creating or updating a CostEstimation record """
    if instance.base_supply:
        instance.material_type = instance.base_supply.material_type
        instance.supply_number = instance.base_supply.supply_number
        instance.supply_name = instance.base_supply.supply_name
        instance.unit = instance.base_supply.unit

@receiver(post_save, sender=BaseSupply)
def update_cost_estimation_on_base_change(sender, instance, **kwargs):
    """ Update all related CostEstimation records when BaseSupply changes """
    CostEstimation.objects.filter(base_supply=instance).update(
        material_type=instance.material_type,
        supply_number=instance.supply_number,
        supply_name=instance.supply_name,
        unit=instance.unit
    )
