# Generated by Django 5.1.2 on 2024-12-12 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0008_remove_auction_user_auction_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='end_date_time',
            field=models.DateTimeField(default='2024-12-31 23:59:59'),
            preserve_default=False,
        ),
    ]