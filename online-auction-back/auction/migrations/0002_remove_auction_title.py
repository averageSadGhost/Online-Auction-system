# Generated by Django 5.1.2 on 2024-10-29 17:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='auction',
            name='title',
        ),
    ]
