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

        
    