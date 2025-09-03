import random
from copy import deepcopy
from .random_seed import get_daily_seed
from Blog.models import DWDino

def distorsion_terrain():
    seed = get_daily_seed("distorsion_terrain")
    rand = random.Random(seed)
    ids = [dino.id for dino in DWDino.objects.all()]
    # for each stat (6 stats), rearange the array of nb_dinos ids
    rearanged_stats = {'base_hp':[], 'base_atk':[], 'base_def':[], 'base_spd':[], 'base_crit':[], 'base_crit_dmg':[]}
    for key in rearanged_stats.keys():
        rand.shuffle(ids)
        for id in ids:
            dino = DWDino.objects.get(id=id)
            rearanged_stats[key].append(getattr(dino, key))
    return [dino.id for dino in DWDino.objects.all()], rearanged_stats

def lac_putrefie_terrain():
    """Lac Putréfié: Tous les Dinos perdent 5% de leur vie max chaque seconde"""
    # This terrain effect is handled in the battle logic via scheduled actions
    return None

def brouillard_epais_terrain():
    """Brouillard Epais: Réduit de 50% la précision de tous les Dinos"""
    # This terrain effect is handled in the load_dino_from_model function
    return None

def jungle_perfide_terrain():
    """Jungle Perfide: Cooldown réduit de 20% pour les Dinos Support"""
    # This terrain effect is handled in the battle logic for support abilities
    return None

def ere_glaciaire_terrain():
    """Ere Glaciaire: Tous les Dinos débutent à 1.0 de vitesse"""
    # This terrain effect is handled in the views and load_dino_from_model function
    return None

def montagne_rocheuse_terrain():
    """Montagne Rocheuse: +10% de défense pour les Dinos Tank, -20% d'attaque pour les Dinos DPS"""
    # This terrain effect is handled in the views and load_dino_from_model function
    return None

def erruption_volcanique_terrain():
    """Erruption Volcanique: +10% d'attaque pour les Dinos DPS, -20% de défense pour les Dinos Tank"""
    # This terrain effect is handled in the views and load_dino_from_model function
    return None

        
    