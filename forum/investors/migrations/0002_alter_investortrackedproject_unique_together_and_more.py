# Generated by Django 4.2.19 on 2025-03-16 09:57

from decimal import Decimal

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investors', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='investortrackedproject',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='investortrackedproject',
            name='share',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), help_text='Share of investment in percentage (0 - 100%)', max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AddConstraint(
            model_name='investortrackedproject',
            constraint=models.UniqueConstraint(fields=('investor', 'project'), name='unique_investor_project'),
        ),
    ]
