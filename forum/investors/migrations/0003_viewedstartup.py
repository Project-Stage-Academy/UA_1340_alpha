# Generated by Django 4.2.19 on 2025-04-01 09:19

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('startups', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('investors', '0002_alter_investortrackedproject_unique_together_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ViewedStartup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('viewed_at', models.DateTimeField(auto_now_add=True)),
                ('startup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='viewed_by', to='startups.startupprofile')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='viewed_startups', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-viewed_at'],
                'unique_together': {('user', 'startup')},
            },
        ),
    ]
