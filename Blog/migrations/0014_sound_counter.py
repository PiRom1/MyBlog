# Generated by Django 5.0.6 on 2024-10-11 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Blog", "0013_sound_usersound"),
    ]

    operations = [
        migrations.AddField(
            model_name="sound",
            name="counter",
            field=models.IntegerField(default=0),
        ),
    ]