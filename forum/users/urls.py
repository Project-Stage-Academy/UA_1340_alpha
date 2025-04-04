from django.urls import include, path

from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView,
    ResendVerificationEmailView,
    ResetPasswordCompleteView,
    ResetPasswordConfirmView,
    ResetPasswordRequestView,
    SelectRoleView,
    SetRoleView,
    SignupView,
    VerifyEmailView,
)

urlpatterns = [
    path("accounts/", include("allauth.urls")),
    path('login/', CustomTokenObtainPairView.as_view(), name='regular-login'),
    path('login/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('select-role/', SelectRoleView.as_view(), name='select_role'),
    path('set-role/', SetRoleView.as_view(), name='set_roles'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("resend-verication-email/", ResendVerificationEmailView.as_view(), name="resend-verification-email"),
    path("reset_password/", ResetPasswordRequestView.as_view(), name="api_reset_password_request"),
    path("reset/<uidb64>/<token>/", ResetPasswordConfirmView.as_view(), name="api_reset_password_confirm"),
    path("reset_password_complete/", ResetPasswordCompleteView.as_view(), name="api_reset_password_complete"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
]
