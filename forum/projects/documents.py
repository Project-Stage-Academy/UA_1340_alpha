from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry

from .models import Project


@registry.register_document
class ProjectDocument(Document):
    class Index:
        name = "projects"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Project
        fields = [
            'title',
            'description',
            'status',
            'funding_goal',
        ]
