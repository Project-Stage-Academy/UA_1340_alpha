from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from elasticsearch_dsl import connections
from .models import Project
from .documents import ProjectDocument


es = connections.get_connection()


@receiver(post_save, sender=Project)
def update_project_index(sender, instance, **kwargs):
    """Update or create an Elasticsearch index entry when a Project is saved."""
    doc = ProjectDocument(
        meta={'id': instance.id},
        id=instance.id,
        title=instance.title,
        description=instance.description,
        funding_goal=float(instance.funding_goal),
        funding_needed=float(instance.funding_needed),
        status=instance.status,
        startup=instance.startup.company_name,
        created_at=instance.created_at,
        updated_at=instance.updated_at
    )
    doc.save()
    print(f"Updated Elasticsearch index for Project {instance.id}")


@receiver(post_delete, sender=Project)
def delete_project_index(sender, instance, **kwargs):
    """Delete an Elasticsearch index entry when a Project is deleted."""
    try:
        es.delete(index="projects", id=instance.id)
        print(f"Deleted Elasticsearch index for Project {instance.id}")
    except Exception as e:
        print(f"Error deleting Elasticsearch index for Project {instance.id}: {e}")
