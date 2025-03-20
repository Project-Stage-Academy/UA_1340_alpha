from django.urls import path

from .views import StartupProfileDetailAPIView, StartupProfileListCreateAPIView

urlpatterns = [
    path('', StartupProfileListCreateAPIView.as_view(), name='startup-list-create'),
    path('<int:pk>/', StartupProfileDetailAPIView.as_view(), name='startup-detail'),
]
