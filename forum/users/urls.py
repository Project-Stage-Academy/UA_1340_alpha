from django.urls import path
from .views import SignupView

urlpatters = [
    path('signup/', SignupView.as_view(), name='signup')
]
