# Generated by Django 5.0.6 on 2024-10-09 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Blog", "0011_user_yoda_counter"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="enjoy_counter",
            field=models.IntegerField(default=0, verbose_name="Enjoy_counter"),
        ),
    ]
