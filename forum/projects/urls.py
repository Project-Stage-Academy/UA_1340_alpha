from django.urls import path

from .views import ProjectDetailAPIView, ProjectListCreateAPIView
from .viewsets import ProjectSearchView

urlpatterns = [
    path('', ProjectListCreateAPIView.as_view(), name='project-list-create'),
    path('<int:pk>/', ProjectDetailAPIView.as_view(), name='project-detail'),
    path('search/', ProjectSearchView.as_view(), name='project-search'),

]
