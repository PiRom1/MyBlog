# Generated by Django 5.0.6 on 2024-10-29 16:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Blog", "0022_borderimage_alter_background_name_alter_box_image_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="markethistory",
            name="item",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="Blog.item"
            ),
        ),
    ]
