from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .documents import ProjectDocument
from .models import Project
from .tasks import send_project_update


@receiver(post_save, sender=Project)
def combined_project_update(sender, instance, created, **kwargs):
    """
    Combined signal handler for project updates.

    This function is triggered after a Project instance is saved. It performs the following actions:
    - Sends an asynchronous update notification using Celery.
    - Sends an update message to the corresponding WebSocket group.
    - Updates the Elasticsearch document for the Project model.

    Args:
        sender (Model): The model class that sent the signal.
        instance (Project): The instance of the Project that was saved.
        created (bool): A flag indicating whether a new instance was created.
        **kwargs: Additional keyword arguments passed to the receiver.
    """
    # Celery update
    send_project_update.delay(
        str(instance.id),
        instance.title,
        instance.description
    )

    # WebSocket update
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'project_{instance.id}',
        {
            'type': 'project_update',
            'message': {
                'id': str(instance.id),
                'title': instance.title,
                'description': instance.description,
            }
        }
    )

    # Elasticsearch document update
    ProjectDocument().save(instance)


@receiver(post_delete, sender=Project)
def delete_project_document(sender, instance, **kwargs):
    """
    Signal to delete the Elasticsearch document for the Project model when an instance is deleted.

    Args:
        sender: The model class.
        instance: The instance being deleted.
        kwargs: Additional keyword arguments.
    """
    ProjectDocument().delete(instance, ignore=404)