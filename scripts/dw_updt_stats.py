from Blog.utils.dw_battle_logic import *
from Blog.models import DWUserDino, DWUserTeam, User, DWDino
from Blog.views.dinowars_views import calculate_total_stats
import pandas as pd

def run():
    # Stats to update (dino_name, stat_name, stat_value)
    stats_to_update = [
        ('Velociraptor', 'hp', 1000),
        ('Velociraptor', 'crit', -0.04)
    ]
    
    for dino_name, stat_name, stat_value in stats_to_update:
        usr_dinos = DWUserDino.objects.filter(dino__name=dino_name)
        for dino in usr_dinos :        
            if stat_name in ['hp', 'atk', 'defense']:
                lvl = dino.level
                old_stat = getattr(dino, stat_name)
                new_stat = old_stat + int(stat_value * pow(1.1, lvl - 1))
                setattr(dino, stat_name, new_stat)
                dino.save()
            else:
                old_stat = getattr(dino, stat_name)
                new_stat = old_stat + stat_value
                setattr(dino, stat_name, new_stat)
                dino.save()

        dino = DWDino.objects.get(name=dino_name)
        stat_name = 'base_' + stat_name
        old_stat = getattr(dino, stat_name)
        new_stat = old_stat + stat_value
        setattr(dino, stat_name, new_stat)
        dino.save()