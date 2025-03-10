from .views import ResetPasswordRequestView, ResetPasswordConfirmView, ResetPasswordCompleteView
from django.urls import path

urlpatterns = [
    path("reset_password/", ResetPasswordRequestView.as_view(),
         name="api_reset_password_request"),
    path("reset/<uidb64>/<token>/", ResetPasswordConfirmView.as_view(),
         name="api_reset_password_confirm"),
    path("reset_password_complete/", ResetPasswordCompleteView.as_view(),
         name="api_reset_password_complete"),
]
