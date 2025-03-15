from django.urls import path
from .views import (
    InvestorProfileApiView,
    InvestorProfileDetailApiView,
    InvestorPreferredIndustryApiView,
    InvestorPreferredIndustryDetailApiView,
    InvestorSavedStartupApiView,
    InvestorSavedStartupDetailApiView,
    InvestorTrackedProjectApiView,
    InvestorTrackedProjectDetailApiView
)

urlpatterns = [
    # Investor Profiles
    path('investor-profiles/', InvestorProfileApiView.as_view(), name='investor-profiles'),
    path('investor-profiles/<int:pk>/', InvestorProfileDetailApiView.as_view(), name='investor-profile-detail'),

    # Investor Preferred Industries
    path('investor-preferred-industries/', InvestorPreferredIndustryApiView.as_view(), name='investor-preferred-industries'),
    path('investor-preferred-industries/<int:pk>/', InvestorPreferredIndustryDetailApiView.as_view(), name='investor-preferred-industry-detail'),

    # Investor Saved Startups
    path('investor-saved-startups/', InvestorSavedStartupApiView.as_view(), name='investor-saved-startups'),
    path('investor-saved-startups/<int:pk>/', InvestorSavedStartupDetailApiView.as_view(), name='investor-saved-startup-detail'),

    # Investor Tracked Projects
    path('investor-tracked-projects/', InvestorTrackedProjectApiView.as_view(), name='investor-tracked-projects'),
    path('investor-tracked-projects/<int:pk>/', InvestorTrackedProjectDetailApiView.as_view(), name='investor-tracked-project-detail'),
]
