# Generated by Django 4.2.1 on 2024-02-28 13:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('guides', '0002_game_guide_new_user_content_creator_newsection_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='guide',
            name='likes',
        ),
        migrations.RemoveField(
            model_name='new',
            name='likes',
        ),
    ]
