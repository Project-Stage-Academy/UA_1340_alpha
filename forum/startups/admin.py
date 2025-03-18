from django.contrib import admin

from startups.models import StartupProfile


@admin.register(StartupProfile)
class StartupProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name',)
    fields = ('company_name', 'startup_logo')