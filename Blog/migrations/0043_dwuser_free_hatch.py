# Generated by Django 5.1.5 on 2025-04-02 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Blog', '0042_alter_dwdinoitem_slot'),
    ]

    operations = [
        migrations.AddField(
            model_name='dwuser',
            name='free_hatch',
            field=models.IntegerField(default=0),
        ),
    ]
