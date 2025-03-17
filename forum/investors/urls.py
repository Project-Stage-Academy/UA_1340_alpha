from django.urls import path

from .views import SavedStartupsApiView

urlpatterns = [
    # Investor Saved Startups
    path('saved-startups/', SavedStartupsApiView.as_view(), name='saved-startups'),
]
