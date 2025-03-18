from django.urls import path

from .views import (
    LogoutAPIView,
    ResetPasswordCompleteView,
    ResetPasswordConfirmView,
    ResetPasswordRequestView,
    SignupView,
)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path("reset_password/", ResetPasswordRequestView.as_view(), name="api_reset_password_request"),
    path("reset/<uidb64>/<token>/", ResetPasswordConfirmView.as_view(), name="api_reset_password_confirm"),
    path("reset_password_complete/", ResetPasswordCompleteView.as_view(), name="api_reset_password_complete")
]
