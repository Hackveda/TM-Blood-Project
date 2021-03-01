from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Label , AlternateLabel

@receiver(post_save, sender=Label)
def create_alternatelabel(sender, instance, created, **kwargs):
    """
    when label is created an alternate label with name as label is also created
    """
    if created:
        AlternateLabel.objects.get_or_create(
            name = instance.name,
            label = instance
        )
@receiver(post_save, sender=Label)
def save_alternatelabel(sender, instance, created, **kwargs):
    """
    when label is saved an alternate label with name as label is also saved
    """
    print('this is instance', instance)
    AlternateLabel.objects.get_or_create(
        name=instance.name,
        label = instance
    )
