from django.urls import path
from .views import ProjectListCreateAPIView, ProjectDetailAPIView

urlpatterns = [
    path('', ProjectListCreateAPIView.as_view(), name='project-list-create'),
    path('<int:pk>/', ProjectDetailAPIView.as_view(), name='project-detail'),
]
