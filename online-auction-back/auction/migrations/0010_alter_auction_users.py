# Generated by Django 5.1.2 on 2024-12-12 08:49

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0009_auction_end_date_time'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='users',
            field=models.ManyToManyField(blank=True, related_name='auctions', to=settings.AUTH_USER_MODEL),
        ),
    ]
