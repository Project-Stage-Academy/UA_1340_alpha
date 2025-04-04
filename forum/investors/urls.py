from django.urls import path

from .views import (
    ClearViewedStartups,
    CreateDeleteSavedStartupApiView,
    InvestorPreferredIndustryApiView,
    InvestorPreferredIndustryDetailApiView,
    InvestorProfileApiView,
    InvestorProfileDetailApiView,
    InvestorTrackedProjectApiView,
    InvestorTrackedProjectDetailApiView,
    LogStartupView,
    RecentlyViewedStartupsView,
    SavedStartupsApiView,
    SubscriptionCreateView,
)

urlpatterns = [
    # Investor Profiles
    path('investor-profiles/', InvestorProfileApiView.as_view(), name='investor-profiles'),
    path('investor-profiles/<int:pk>/', InvestorProfileDetailApiView.as_view(), name='investor-profile-detail'),

    # Investor Preferred Industries
    path('investor-preferred-industries/', InvestorPreferredIndustryApiView.as_view(),
         name='investor-preferred-industries'),
    path('investor-preferred-industries/<int:pk>/', InvestorPreferredIndustryDetailApiView.as_view(),
         name='investor-preferred-industry-detail'),

    # Investor Tracked Projects
    path('investor-tracked-projects/', InvestorTrackedProjectApiView.as_view(), name='investor-tracked-projects'),
    path('investor-tracked-projects/<int:pk>/', InvestorTrackedProjectDetailApiView.as_view(),
         name='investor-tracked-project-detail'),

    # Investor Saved Startups
    path('saved-startups/', SavedStartupsApiView.as_view(), name='saved-startups'),
    path('saved-startups/<int:startup_id>/', CreateDeleteSavedStartupApiView.as_view(), name='save-delete-startup'),

    # Investor Subscription
    path('subscribe/', SubscriptionCreateView.as_view(), name='subscribe'),

    # Investor Viewed Startups
    path('viewed-startups/', RecentlyViewedStartupsView.as_view(), name='viewed-startups'),
    path('viewed-startups/<int:startup_id>', LogStartupView.as_view(), name='save-viewed-startup'),
    path('viewed-startups/clear', ClearViewedStartups.as_view(), name='clear-viewed-startups'),

]
