from django.core.management import BaseCommand
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from projects.models import Project


class Command(BaseCommand):
    help = 'Bulk index all projects in Elasticsearch'

    def handle(self, *args, **options):
        es = Elasticsearch(["http://127.0.0.1:9200"])

        actions = ({
            "_index": "projects",
            "_id": project.id,
            "_source": {
                "title": project.title,
                "description": project.description,
                "status": project.status,
                "funding_goal": project.funding_goal
            }
        } for project in Project.objects.all().iterator())

        success, failed = bulk(es, actions, stats_only=True)
        self.stdout.write(
            self.style.SUCCESS(f"Indexed {success} projects. Failures: {failed}")
        )
