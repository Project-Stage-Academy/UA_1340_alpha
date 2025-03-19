from django.urls import path

from .views import CreateDeleteSavedStartupApiView, SavedStartupsApiView

urlpatterns = [
    # Investor Saved Startups
    path('saved-startups/', SavedStartupsApiView.as_view(), name='saved-startups'),
    path('saved-startups/<int:startup_id>/', CreateDeleteSavedStartupApiView.as_view(), name='save-delete-startup'),
]
