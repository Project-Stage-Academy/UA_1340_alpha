from django.urls import path
from .views import StartupProfileListCreateAPIView, StartupProfileDetailAPIView

urlpatterns = [
    path('', StartupProfileListCreateAPIView.as_view(), name='startup-list-create'),
    path('<int:pk>/', StartupProfileDetailAPIView.as_view(), name='startup-detail'),
]
