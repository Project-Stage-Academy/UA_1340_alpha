from django.apps import AppConfig
from django.db.models.signals import post_save, post_delete

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

        from .signals import (  # Import your signals module
            celery_project_update,
            websocket_project_update,
            update_project_document,
            delete_project_document
        )
        post_save.connect(celery_project_update, sender='projects.Project')
        post_save.connect(websocket_project_update, sender='projects.Project')
        post_save.connect(update_project_document, sender='projects.Project')
        post_delete.connect(delete_project_document, sender='projects.Project')
