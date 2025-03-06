# Generated by Django 4.2.19 on 2025-03-06 17:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        ('projects', '0001_initial'),
        ('startups', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvestorProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('company_name', models.CharField(max_length=255)),
                ('investment_focus', models.CharField(max_length=255)),
                ('contact_email', models.EmailField(max_length=254, unique=True)),
                ('investment_range', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='investor_profile', to='users.user')),
            ],
        ),
        migrations.CreateModel(
            name='InvestorTrackedProject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('investor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tracked_projects', to='investors.investorprofile')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='investor_tracks', to='projects.project')),
            ],
            options={
                'unique_together': {('investor', 'project')},
            },
        ),
        migrations.CreateModel(
            name='InvestorSavedStartup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('investor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='saved_startups', to='investors.investorprofile')),
                ('startup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='investor_saves', to='startups.startupprofile')),
            ],
            options={
                'unique_together': {('investor', 'startup')},
            },
        ),
        migrations.CreateModel(
            name='InvestorPreferredIndustry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('industry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='investors', to='startups.industry')),
                ('investor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='preferred_industries', to='investors.investorprofile')),
            ],
            options={
                'unique_together': {('investor', 'industry')},
            },
        ),
    ]
