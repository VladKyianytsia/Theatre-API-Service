# Generated by Django 5.0.3 on 2024-03-27 14:20

import theatre.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theatre', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='play',
            name='image',
            field=models.ImageField(null=True, upload_to=theatre.models.play_image_path),
        ),
    ]
