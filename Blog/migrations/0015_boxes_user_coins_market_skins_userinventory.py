# Generated by Django 5.1 on 2024-10-15 13:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Blog', '0014_sound_counter'),
    ]

    operations = [
        migrations.CreateModel(
            name='Boxes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='name')),
                ('image', models.ImageField(upload_to='')),
                ('price', models.IntegerField(default=200, verbose_name='price')),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='coins',
            field=models.IntegerField(default=0, verbose_name='Diplodocoins'),
        ),
        migrations.CreateModel(
            name='Market',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('skin', 'Skin'), ('box', 'Box')], default='box', max_length=4, verbose_name='type')),
                ('item_id', models.IntegerField(default=-1, verbose_name='item_id')),
                ('price', models.IntegerField(default=100, verbose_name='price')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Skins',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='name')),
                ('image', models.ImageField(upload_to='')),
                ('pattern', models.CharField(blank=True, max_length=7, verbose_name='pattern')),
                ('box', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Blog.boxes')),
            ],
        ),
        migrations.CreateModel(
            name='UserInventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('skin', 'Skin'), ('box', 'Box')], default='box', max_length=4, verbose_name='type')),
                ('item_id', models.IntegerField(default=-1, verbose_name='item_id')),
                ('status', models.CharField(choices=[('equipped', 'Equipped'), ('unequipped', 'Unequipped'), ('locked', 'Locked')], default='unequipped', max_length=10, verbose_name='status')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]