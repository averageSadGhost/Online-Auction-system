# Generated by Django 5.1.2 on 2024-12-05 07:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0005_alter_auction_users'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='auction',
            name='created_by',
        ),
    ]
