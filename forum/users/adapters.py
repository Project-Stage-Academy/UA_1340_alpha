from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.http import HttpResponseRedirect
from django.urls import reverse, Resolver404


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        if sociallogin.is_existing:
            return
        request.session['sociallogin'] = sociallogin.serialize()
        try:
            reverse('set_roles')  
        except Resolver404:
            raise ImmediateHttpResponse(HttpResponseRedirect(reverse('home')))  
        raise ImmediateHttpResponse(HttpResponseRedirect(reverse('set_roles')))

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        user.is_email_confirmed = True
        user.save()
        request.session.pop('sociallogin', None)
        return user
    