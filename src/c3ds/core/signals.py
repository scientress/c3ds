import channels.layers
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.dispatch import receiver
from c3ds.core.models import BaseView, Display


channel_layer = channels.layers.get_channel_layer()


@receiver(post_save, sender=Display)
def display_saved_handler(sender: Display, instance: Display, created: bool, updated_fields=None, **kwargs):
    async_to_sync(channel_layer.group_send)(f'display_{instance.slug}', {'type': 'cmd', 'cmd': 'reload'})

@receiver(post_save)
def view_saved_handler(sender: BaseView, instance: BaseView = None, created: bool = None, updated_fields=None, **kwargs):
    if not isinstance(instance, BaseView):
        return
    for display in instance.displays.all():
        async_to_sync(channel_layer.group_send)(f'display_{display.slug}', {'type': 'cmd', 'cmd': 'reload'})
