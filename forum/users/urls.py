from django.urls import path
from .views import SignupView, LogoutAPIView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
]
