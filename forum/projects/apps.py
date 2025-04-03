from django.apps import AppConfig
from django.db.models.signals import post_delete, post_save


class ProjectsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'projects'

    def ready(self):
        """
        This method is called when the application is ready. It is used to import signal handlers
        and perform any necessary setup for the application.

        In this case, it imports the signal handlers from the signals module to ensure they are
        registered and ready to handle signals.
        """
        import projects.signals
        from .signals import (
            combined_project_update,
            delete_project_document,
        )
        post_save.connect(combined_project_update, sender='projects.Project')
        post_delete.connect(delete_project_document, sender='projects.Project')