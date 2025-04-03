from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .documents import ProjectDocument
from .models import Project
from .tasks import send_project_update


@receiver(post_save, sender=Project)
def celery_project_update(sender, instance, created, **kwargs):
    """
    Sends an asynchronous update notification when a Project is created or updated.

    This function is triggered automatically whenever a Project instance is saved. It sends
    an asynchronous task to notify interested parties about the updated or newly created project
    using the `send_project_update` Celery task. The task sends information such as the project's
    ID, title, and description.

    Args:
        sender (Model class): The model class (Project) that triggered this signal.
        instance (Project): The specific instance of the Project model that was saved.
        created (bool): A boolean indicating if the instance was created (True) or updated (False).
        **kwargs: Additional keyword arguments passed by the signal.
    """
    send_project_update.delay(
        str(instance.id),
        instance.title,
        instance.description
    )


@receiver(post_save, sender=Project)
def websocket_project_update(sender, instance, created, **kwargs):
    """
    Signal receiver for project updates.

    This function is triggered after a Project instance is saved. It sends
    an update message to the corresponding WebSocket group, notifying
    connected clients of the project's latest details.

    Args:
        sender (Model): The model class that sent the signal.
        instance (Project): The instance of the Project that was saved.
        created (bool): A flag indicating whether a new instance was created.
        **kwargs: Additional keyword arguments passed to the receiver.
    """
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


@receiver(post_save, sender=Project)
def update_project_document(sender, instance, **kwargs):
    """
    Signal to update the Elasticsearch document for the Project model when an instance is saved.

    Args:
        sender: The model class.
        instance: The instance being saved.
        kwargs: Additional keyword arguments.
    """
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
    ProjectDocument().delete(instance)
