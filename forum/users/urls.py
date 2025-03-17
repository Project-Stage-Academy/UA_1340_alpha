from django.urls import path

from .views import (ResendVerificationEmailView, ResetPasswordCompleteView,
                    ResetPasswordConfirmView, ResetPasswordRequestView,
                    SignupView, VerifyEmailView)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path("resend-verication-email/", ResendVerificationEmailView.as_view(), name="resend-verification-email"),
    path("reset_password/", ResetPasswordRequestView.as_view(), name="api_reset_password_request"),
    path("reset/<uidb64>/<token>/", ResetPasswordConfirmView.as_view(), name="api_reset_password_confirm"),
    path("reset_password_complete/", ResetPasswordCompleteView.as_view(), name="api_reset_password_complete"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
]
