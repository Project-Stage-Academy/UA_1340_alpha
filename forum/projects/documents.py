from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from startups.models import StartupProfile
from .models import Project


@registry.register_document
class ProjectDocument(Document):
    startup_name = fields.TextField(attr='startup.company_name')
    created_at = fields.DateField()

    class Index:
        name = 'projects'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = Project
        fields = ['title', 'description', 'status', 'funding_goal', 'duration']
        related_models = [StartupProfile]

    def get_queryset(self):
        return super().get_queryset().select_related('startup')

    def get_instances_from_related(self, related):
        return related.projects.all()

