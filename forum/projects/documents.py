from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Project


@registry.register_document
class ProjectDocument(Document):
    startup = fields.ObjectField(properties={
        'company_name': fields.TextField(),
        'id': fields.IntegerField(),
    })

    class Index:
        name = 'projects'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Project
        fields = [
            'title',
            'description',
            'status',
            'funding_goal',
            'duration',
            'created_at',
        ]

    def get_queryset(self):
        return super().get_queryset().select_related('startup')
