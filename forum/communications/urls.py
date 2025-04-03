from django.urls import path
from .views import CreateConversationApiView, SendMessageApiView, ListMessagesApiView

urlpatterns = [
    path('conversations/', CreateConversationApiView.as_view(), name='create_conversation'),
    path('messages/', SendMessageApiView.as_view(), name='send_message'),
    path('conversations/<str:conversation_id>/messages/', ListMessagesApiView.as_view(), name='list_messages'),
]
