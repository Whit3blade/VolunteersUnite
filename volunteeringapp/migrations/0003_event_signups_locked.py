# Generated by Django 4.2.9 on 2024-08-23 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volunteeringapp', '0002_remove_organizer_profile_photo_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='signups_locked',
            field=models.BooleanField(default=False),
        ),
    ]
