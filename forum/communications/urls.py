from django.urls import path
from .views import CommunicationsApiView, CommunicationDetailApiView

urlpatterns = [
    path('', CommunicationsApiView.as_view(), name='communications-list-create'),
    path('<int:communication_id>/', CommunicationDetailApiView.as_view(), name='communication-detail'),
]
