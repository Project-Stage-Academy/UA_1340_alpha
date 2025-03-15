from django.contrib import admin
from django.urls import path, include
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from users.views import SendEmailAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/users/', include('users.urls')),
    path('send-email/', SendEmailAPIView.as_view(), name="send_email"),
    path('api/communications/', include('communications.urls')),
    path('api/investors/', include('investors.urls')),
]
