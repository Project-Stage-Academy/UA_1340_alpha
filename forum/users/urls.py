from django.urls import path
from .views import SignupView, ResetPasswordRequestView, ResetPasswordConfirmView, ResetPasswordCompleteView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path("reset_password/", ResetPasswordRequestView.as_view(), name="api_reset_password_request"),
    path("reset/<uidb64>/<token>/", ResetPasswordConfirmView.as_view(), name="api_reset_password_confirm"),
    path("reset_password_complete/", ResetPasswordCompleteView.as_view(), name="api_reset_password_complete")
]
