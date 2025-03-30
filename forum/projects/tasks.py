import logging
from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


@shared_task
def send_project_update(id, title, description):
    """
    Sends a real-time update notification for a specific project via WebSockets.

    This function is designed to be executed asynchronously using Celery. It sends
    a WebSocket message containing the project ID, title, and description to a specific
    channel group, identified by the project's ID. The function uses Django Channels
    to communicate with the WebSocket layer, ensuring that all clients subscribed to
    the project channel receive the update.

    Args:
        id (str): The unique identifier of the project being updated.
        title (str): The title of the project.
        description (str): A brief description of the project's updates.

    Logs:
        Logs a message indicating that the update was sent for the project.
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'project_{id}',
        {
            'type': 'project_update',
            'message': {
                'id': str(id),
                'title': title,
                'description': description,
            }
        }
    )

    logging.info(f"Update sent for project: {id}")