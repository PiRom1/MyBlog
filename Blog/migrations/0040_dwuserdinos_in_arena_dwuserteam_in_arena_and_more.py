# Generated by Django 5.1.5 on 2025-03-27 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Blog', '0039_dwattack_dwfight_dwdino_dwuser_dwuserdinos_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='dwuserdino',
            name='in_arena',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='dwuserteam',
            name='in_arena',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='dwuserteam',
            name='name',
            field=models.CharField(default='Team1', max_length=20),
            preserve_default=False,
        ),
    ]
