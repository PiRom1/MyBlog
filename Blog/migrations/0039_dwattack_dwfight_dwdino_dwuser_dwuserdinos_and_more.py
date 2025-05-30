# Generated by Django 5.1.5 on 2025-03-26 17:04

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Blog', '0038_alter_message_pub_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='DWAttack',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('atk_mult_low', models.FloatField(default=0.5)),
                ('atk_mult_high', models.FloatField(default=1.5)),
                ('spe_effect', models.TextField(default='')),
            ],
        ),
        migrations.CreateModel(
            name='DWFight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user1', models.CharField(max_length=100)),
                ('user2', models.CharField(max_length=100)),
                ('user1_team', models.CharField(max_length=100)),
                ('user2_team', models.CharField(max_length=100)),
                ('winner', models.CharField(max_length=100)),
                ('gamemode', models.CharField(choices=[('duel', 'Duel'), ('arena', 'Arena')], default='duel', max_length=10)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('logs', models.TextField(default='')),
            ],
        ),
        migrations.CreateModel(
            name='DWDino',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('classe', models.CharField(choices=[('tank', 'Tank'), ('dps', 'DPS'), ('support', 'Support')], default='dps', max_length=10)),
                ('base_hp', models.IntegerField(default=3000)),
                ('base_atk', models.IntegerField(default=100)),
                ('base_def', models.IntegerField(default=100)),
                ('base_spd', models.FloatField(default=1.0)),
                ('base_crit', models.FloatField(default=0.05)),
                ('base_crit_dmg', models.FloatField(default=1.5)),
                ('attack', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Blog.dwattack')),
            ],
        ),
        migrations.CreateModel(
            name='DWUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('elo', models.IntegerField(default=1000)),
                ('wins', models.IntegerField(default=0)),
                ('losses', models.IntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DWUserDino',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.IntegerField(default=1)),
                ('hp', models.IntegerField(default=3000)),
                ('atk', models.IntegerField(default=100)),
                ('defense', models.IntegerField(default=100)),
                ('spd', models.FloatField(default=1.0)),
                ('crit', models.FloatField(default=0.05)),
                ('crit_dmg', models.FloatField(default=1.5)),
                ('attack', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Blog.dwattack')),
                ('dino', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Blog.dwdino')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DWUserTeam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dino1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dino1', to='Blog.dwuserdino')),
                ('dino2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dino2', to='Blog.dwuserdino')),
                ('dino3', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dino3', to='Blog.dwuserdino')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
