import math
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from Blog.models import DWFight, DWPvmTerrain, DWUserDino, DWUserTeam, DWUser, DWPvmRun, DWPvmRunAbility, DWPvmDino, DWPvmNextFightDino, DWPvmNextAbility, DWDino, DWPvmNewRun, DWPvmAbility, DWPvmLeaderboard
from Blog.utils.dw_terrains import distorsion_terrain
from Blog.utils.random_seed import get_daily_seed
from Blog.utils.dw_pvm_battle_logic import load_dino_from_model, GameState
from constance import config as constance_cfg
import json
import random
from django.views.decorators.http import require_POST
from django.db import transaction
import datetime

@login_required
def pvm_view(request):
    # Get current run info if exists
    try:
        run_info = DWPvmRun.objects.get(user=request.user)
        run_abilities = DWPvmRunAbility.objects.filter(run=run_info).select_related('ability').order_by('-id')
        run_dinos = [run_info.dino1, run_info.dino2, run_info.dino3]
        if None in run_dinos:
            raise ValueError("One or more dinos isn't selected.")
        next_fight_dinos = DWPvmNextFightDino.objects.filter(run=run_info).select_related('dino')
        next_abilities = DWPvmNextAbility.objects.filter(run=run_info).select_related('ability')
        life_counter = ''
        for _ in range(run_info.life): life_counter += '1'
        terrain = run_info.terrain
    except (DWPvmRun.DoesNotExist, ValueError) as e:
        return redirect('new_run_view')
    else :    
        context = {
            'run_info': run_info,
            'life_counter': life_counter,
            'run_abilities': run_abilities,
            'run_dinos': run_dinos,
            'next_fight_dinos': next_fight_dinos,
            'next_abilities': next_abilities,
            'terrain': terrain,
        }
        return render(request, 'Blog/dinowars/pvm.html', context)

@login_required
def run_dino_details_view(request, dino_id):
    """View function to display details of a run dino."""
    try:        
        enemy = request.headers['enemy'] == 'true'
        # Get run info for stat points display
        try:
            run_info = DWPvmRun.objects.get(user=request.user)
        except DWPvmRun.DoesNotExist:
            run_info = None

        if enemy:
            if run_info.level < 3: lvl = -3 + run_info.level
            elif run_info.level < 5: lvl = run_info.level - 2
            elif run_info.level < 10: lvl = 2 + 0.5 * (run_info.level - 4)
            elif run_info.level < 15: lvl = 5.5 + 0.5 * (run_info.level - 10)
            elif run_info.level < 20: lvl = 8.5 + 1 * (run_info.level - 15)
            else: lvl = 14 + 1 * (run_info.level - 20)
            # Fetch the enemy dino details
            dino = get_object_or_404(DWPvmNextFightDino, id=dino_id, run__user=request.user)
            hp_lvl = lvl
            atk_lvl = lvl
            defense_lvl = lvl
            spd_lvl = lvl
            crit_lvl = lvl
            crit_dmg_lvl = lvl
        else:
            # Fetch the user's dino details
            dino = get_object_or_404(DWPvmDino, id=dino_id, user=request.user)
            hp_lvl = dino.hp_lvl
            atk_lvl = dino.atk_lvl
            defense_lvl = dino.defense_lvl
            spd_lvl = dino.spd_lvl
            crit_lvl = dino.crit_lvl
            crit_dmg_lvl = dino.crit_dmg_lvl
        
        # Calculate stats for display
        stats = {
            'hp': {'total': dino.hp, 'lvl': hp_lvl},
            'atk': {'total': dino.atk, 'lvl': atk_lvl},
            'defense': {'total': dino.defense, 'lvl': defense_lvl},
            'spd': {'total': dino.spd, 'lvl': spd_lvl},
            'crit': {'total': dino.crit, 'lvl': crit_lvl},
            'crit_dmg': {'total': dino.crit_dmg, 'lvl': crit_dmg_lvl},
            'mean_lvl': round(sum([hp_lvl, atk_lvl, defense_lvl, spd_lvl, crit_lvl, crit_dmg_lvl]) / 6, 2),
        }
        
        # Render the template with the dino details
        return render(request, 'Blog/dinowars/_dino_details_popup_pvm.html', {
            'dino': dino,
            'stats': stats,
            'enemy': enemy,
            'run_info': run_info,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def reward(i):
    return pow(2, math.ceil(i/3)) * (3 + ((i-1) % 3))

def sumreward(i):
    return sum(reward(j) for j in range(1, i+1))

def stat_cost(i):
    return pow(2,i-1)

@login_required
def stat_allocation_view(request, dino_id):
    """View function to display the stat allocation interface for a dino."""
    try:
        # Fetch the dino details
        dino = get_object_or_404(DWPvmDino, id=dino_id, user=request.user)
        
        # Get run info for stat points
        run_info = get_object_or_404(DWPvmRun, user=request.user)
        
        # Get current stat levels for display
        stat_levels = {
            'hp_lvl': dino.hp_lvl,
            'atk_lvl': dino.atk_lvl,
            'defense_lvl': dino.defense_lvl,
            'spd_lvl': dino.spd_lvl,
            'crit_lvl': dino.crit_lvl,
            'crit_dmg_lvl': dino.crit_dmg_lvl,
        }
        
        # Calculate the cost for leveling up each stat
        stat_costs = {
            'hp_cost': stat_cost(stat_levels['hp_lvl']),
            'atk_cost': stat_cost(stat_levels['atk_lvl']),
            'defense_cost': stat_cost(stat_levels['defense_lvl']),
            'spd_cost': stat_cost(stat_levels['spd_lvl']),
            'crit_cost': stat_cost(stat_levels['crit_lvl']),
            'crit_dmg_cost': stat_cost(stat_levels['crit_dmg_lvl']),
        }
        
        return render(request, 'Blog/dinowars/_stat_points_allocation_popup.html', {
            'dino': dino,
            'run_info': run_info,
            'stat_levels': stat_levels,
            'stat_costs': stat_costs,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_POST
def level_up_stat_view(request, dino_id, stat_name):
    """View function to handle leveling up a specific stat."""
    try:        
        # Fetch the dino and run info
        dino = get_object_or_404(DWPvmDino, id=dino_id, user=request.user)
        run_info = get_object_or_404(DWPvmRun, user=request.user)

        stat_name_lvl = f"{stat_name}_lvl"
        cost = stat_cost(getattr(dino, stat_name_lvl))
        
        # Check if enough stat points are available
        if run_info.stat_points < cost:
            return JsonResponse({'success': False, 'error': 'Pas assez de points de statistiques disponibles!'})
        
        # Update the appropriate stat level and value
        if stat_name == 'hp':
            dino.hp += dino.hp/(dino.hp_lvl+9)
            dino.hp_lvl += 1
        elif stat_name == 'atk':
            dino.atk += dino.atk/(dino.atk_lvl+9)
            dino.atk_lvl += 1
        elif stat_name == 'defense':
            dino.defense += dino.defense/(dino.defense_lvl+9)
            dino.defense_lvl += 1
        elif stat_name == 'spd':
            dino.spd_lvl += 1
            dino.spd += 0.1
            dino.spd = round(dino.spd, 1)
        elif stat_name == 'crit':
            dino.crit_lvl += 1
            dino.crit += 0.04
            dino.crit = round(dino.crit, 2)
        elif stat_name == 'crit_dmg':
            dino.crit_dmg_lvl += 1
            dino.crit_dmg += 0.1
            dino.crit_dmg = round(dino.crit_dmg, 1)
        else:
            return JsonResponse({'success': False, 'error': 'Statistique invalide!'})
        
        # Deduct stat points and save both objects
        run_info.stat_points -= cost
        run_info.save()
        dino.save()
        
        return JsonResponse({
            'success': True,
            'remaining_points': run_info.stat_points,
            'stat_name': stat_name,
            'new_level': getattr(dino, f'{stat_name}_lvl'),
            'new_value': getattr(dino, stat_name),
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@require_POST
def select_ability_view(request, ability_id):
    """View function to handle ability selection."""
    try:
        # Fetch the ability from the next abilities
        next_ability = get_object_or_404(DWPvmNextAbility, id=ability_id, run__user=request.user)
        run_info = next_ability.run
        
        # Create a new run ability based on the selected next ability
        run_ability = DWPvmRunAbility.objects.create(
            run=run_info,
            ability=next_ability.ability
        )
        
        # Instead of deleting, mark this as selected (we'll add this field to the model)
        next_ability.is_selected = True
        next_ability.save()
        
        # Mark other abilities as discarded
        DWPvmNextAbility.objects.filter(run=run_info).exclude(id=ability_id).update(is_discarded=True)
        
        return JsonResponse({
            'success': True,
            'ability_name': run_ability.ability.name,
            'ability_description': run_ability.ability.description,
            'ability_id': run_ability.id,
            'next_ability_id': next_ability.id,
            'to_dino': next_ability.ability.to_dino  # Include to_dino field
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@require_POST
def select_ability_dino_view(request, ability_id):
    """View function to associate a dino with an ability."""
    try:
        # Parse the request data
        data = json.loads(request.body)
        dino_id = data.get('dino_id')
        
        # Fetch the run ability and the dino
        run_ability = get_object_or_404(DWPvmRunAbility, id=ability_id, run__user=request.user)
        dino = get_object_or_404(DWPvmDino, id=dino_id, user=request.user)
        
        # Associate the dino with the ability
        run_ability.dino = dino
        run_ability.save()
        
        return JsonResponse({
            'success': True,
            'ability_id': run_ability.id,
            'dino_id': dino.id,
            'dino_name': dino.dino.name
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def set_new_run_dinos(new_run, random_dinos):
    """Helper function to set new run dinos."""
    terrain = new_run.terrain
    dinos_stats = {'dino1': {}, 'dino2': {}, 'dino3': {}}
    if terrain.name == "Distorsion Spatio-Temporelle":
        ids, rearanged_stats = distorsion_terrain()
        for i, dino in enumerate(random_dinos):
            index = ids.index(dino.id)
            dino_stats = {
                'hp': rearanged_stats['base_hp'][index],
                'atk': rearanged_stats['base_atk'][index],
                'defense': rearanged_stats['base_def'][index],
                'spd': rearanged_stats['base_spd'][index],
                'crit': rearanged_stats['base_crit'][index],
                'crit_dmg': rearanged_stats['base_crit_dmg'][index]
            }
            dinos_stats[f'dino{i+1}'] = dino_stats
    else:
        for i, dino in enumerate(random_dinos):
            dino_stats = {
                'hp': dino.base_hp,
                'atk': dino.base_atk,
                'defense': dino.base_def,
                'spd': 1.0 if terrain.name == "Ere Glaciaire" else dino.base_spd,
                'crit': dino.base_crit,
                'crit_dmg': dino.base_crit_dmg
            }
            
            dinos_stats[f'dino{i+1}'] = dino_stats

    new_run.dino1 = DWPvmDino.objects.create(
        user=new_run.user,
        dino=random_dinos[0],
        hp=dinos_stats['dino1']['hp'],
        atk=dinos_stats['dino1']['atk'],
        defense=dinos_stats['dino1']['defense'],
        spd=dinos_stats['dino1']['spd'],
        crit=dinos_stats['dino1']['crit'],
        crit_dmg=dinos_stats['dino1']['crit_dmg'],
        hp_lvl=1,
        atk_lvl=1,
        defense_lvl=1,
        spd_lvl=1,
        crit_lvl=1,
        crit_dmg_lvl=1,
        attack=random_dinos[0].attack
    )
    new_run.dino2 = DWPvmDino.objects.create(
        user=new_run.user,
        dino=random_dinos[1],
        hp=dinos_stats['dino2']['hp'],
        atk=dinos_stats['dino2']['atk'],
        defense=dinos_stats['dino2']['defense'],
        spd=dinos_stats['dino2']['spd'],
        crit=dinos_stats['dino2']['crit'],
        crit_dmg=dinos_stats['dino2']['crit_dmg'],
        hp_lvl=1,
        atk_lvl=1,
        defense_lvl=1,
        spd_lvl=1,
        crit_lvl=1,
        crit_dmg_lvl=1,
        attack=random_dinos[1].attack
    )
    new_run.dino3 = DWPvmDino.objects.create(
        user=new_run.user,
        dino=random_dinos[2],
        hp=dinos_stats['dino3']['hp'],
        atk=dinos_stats['dino3']['atk'],
        defense=dinos_stats['dino3']['defense'],
        spd=dinos_stats['dino3']['spd'],
        crit=dinos_stats['dino3']['crit'],
        crit_dmg=dinos_stats['dino3']['crit_dmg'],
        hp_lvl=1,
        atk_lvl=1,
        defense_lvl=1,
        spd_lvl=1,
        crit_lvl=1,
        crit_dmg_lvl=1,
        attack=random_dinos[2].attack
    )
    new_run.save()
    return [new_run.dino1, new_run.dino2, new_run.dino3]

def get_random_dinos(all_dinos, new_run):
    step = new_run.state
    date_day = str(datetime.date.today())
    dw_user = DWUser.objects.get(user=new_run.user)
    seed = get_daily_seed(purpose=f"dino_select_{step}", run_number=dw_user.pvm_runs_td, additional=date_day)
    rand = random.Random(seed)
    random_dinos = rand.sample(all_dinos, 3)
    return set_new_run_dinos(new_run, random_dinos)

@login_required
def new_run_view(request):
    """View function to start a new PvM run."""
    # Check if there's an existing run for this user
    try:
        existing_run = DWPvmRun.objects.get(user=request.user)
        run_dinos = [existing_run.dino1, existing_run.dino2, existing_run.dino3]
        if None in run_dinos:
            raise ValueError("One or more dinos isn't selected.")
        return redirect('pvm_view')
    except (DWPvmRun.DoesNotExist, ValueError) as e:
        # Check if there's an existing selection in progress
        try:
            existing_run = DWPvmRun.objects.get(user=request.user)
            new_run = DWPvmNewRun.objects.get(user=request.user)
            terrain = new_run.terrain
            if new_run.state < 4:  # Selection not completed
                random_dinos = [new_run.dino1, new_run.dino2, new_run.dino3]
                selected_dinos = [dino for dino in [existing_run.dino1, existing_run.dino2, existing_run.dino3] if dino is not None]
                print(selected_dinos)
                context = {
                    'random_dinos': random_dinos,
                    'selection_step': new_run.state,
                    'selected_dinos': selected_dinos,
                    'terrain': terrain,
                }
                return render(request, 'Blog/dinowars/new_run.html', context)
        except (DWPvmRun.DoesNotExist, DWPvmNewRun.DoesNotExist) as e:
            pass
    
    # Create a new DWPvmNewRun object for this user
    DWPvmNewRun.objects.filter(user=request.user).delete()  # Clear any existing entries
    
    dw_user = DWUser.objects.get(user=request.user)
    seed = get_daily_seed(purpose=f"terrain_select", additional=str(datetime.date.today()))
    rand = random.Random(seed)
    all_terrains = list(DWPvmTerrain.objects.all())
    rand.shuffle(all_terrains)
    terrain = all_terrains[dw_user.pvm_runs_td % len(all_terrains)]

    new_run = DWPvmNewRun.objects.create(user=request.user, state=1, terrain=terrain)
    final_run = DWPvmRun.objects.create(user=request.user, terrain=terrain)
    
    # Get three random dinos for initial selection
    all_dinos = list(DWDino.objects.all())
    if len(all_dinos) < 3:
        return JsonResponse({'error': 'Not enough dinos in database.'}, status=500)
    
    random_dinos = get_random_dinos(all_dinos, new_run)

    context = {
        'random_dinos': random_dinos,
        'selection_step': 1,
        'selected_dinos': [],
        'terrain': terrain,
    }
    return render(request, 'Blog/dinowars/new_run.html', context)

@login_required
@require_POST
def select_run_dino_view(request):
    """Handle the dino selection process for a new run."""
    try:
        data = json.loads(request.body)
        dino_id = data.get('dino_id')
        dw_user = DWUser.objects.get(user=request.user)
        seed = get_daily_seed(purpose=f"terrain_select", additional=str(datetime.date.today()))
        rand = random.Random(seed)
        all_terrains = list(DWPvmTerrain.objects.all())
        rand.shuffle(all_terrains)
        terrain = all_terrains[dw_user.pvm_runs_td % len(all_terrains)]
        
        # Retrieve or create the DWPvmNewRun object
        try:
            new_run = DWPvmNewRun.objects.get(user=request.user)
            final_run = DWPvmRun.objects.get(user=request.user)
        except DWPvmRun.DoesNotExist:
            final_run = DWPvmRun.objects.create(user=request.user, terrain=terrain)
        except DWPvmNewRun.DoesNotExist:
            new_run = DWPvmNewRun.objects.create(user=request.user, state=1, terrain=terrain)

        # Get selected dino details for display
        selected_dinos = []
        if final_run.dino1:
            selected_dinos.append({
                'id': final_run.dino1.dino.id,
                'name': final_run.dino1.dino.name,
                'hp': final_run.dino1.hp,
                'atk': final_run.dino1.atk,
                'defense': final_run.dino1.defense,
                'spd': final_run.dino1.spd,
                'crit': final_run.dino1.crit,
                'crit_dmg': final_run.dino1.crit_dmg,
                'attack': final_run.dino1.attack.spe_effect,
            })
        if final_run.dino2:
            selected_dinos.append({
                'id': final_run.dino2.dino.id,
                'name': final_run.dino2.dino.name,
                'hp': final_run.dino2.hp,
                'atk': final_run.dino2.atk,
                'defense': final_run.dino2.defense,
                'spd': final_run.dino2.spd,
                'crit': final_run.dino2.crit,
                'crit_dmg': final_run.dino2.crit_dmg,
                'attack': final_run.dino2.attack.spe_effect,
            })
        
        # Add the newly selected dino
        if dino_id:
            selected_dino = get_object_or_404(DWDino, id=dino_id)
            pvm_dino = get_object_or_404(DWPvmDino, dino=selected_dino, user=request.user)
            
            # Update the new_run object based on current state
            if new_run.state == 1:
                final_run.dino1 = pvm_dino
                new_run.state = 2
            elif new_run.state == 2:
                final_run.dino2 = pvm_dino
                new_run.state = 3
            elif new_run.state == 3:
                final_run.dino3 = pvm_dino
                if new_run.dino1 and new_run.dino1 != pvm_dino:
                    new_run.dino1.delete()
                if new_run.dino2 and new_run.dino2 != pvm_dino:
                    new_run.dino2.delete()
                if new_run.dino3 and new_run.dino3 != pvm_dino:
                    new_run.dino3.delete()
                new_run.delete()
                final_run.save()
                set_next_fight_dinos(final_run)
                return JsonResponse({
                    'success': True,
                    'redirect': '/dinowars/pvm/'
                })
            
            new_run.save()
            final_run.save()

            # Add the selected dino to our display list
            selected_dinos.append({
                'id': selected_dino.id,
                'name': selected_dino.name,
                'hp': pvm_dino.hp,
                'atk': pvm_dino.atk,
                'defense': pvm_dino.defense,
                'spd': pvm_dino.spd,
                'crit': pvm_dino.crit,
                'crit_dmg': pvm_dino.crit_dmg,
                'attack': pvm_dino.attack.spe_effect,
            })

        # Delete old dinos from the new_run object
        if new_run.dino1 and new_run.dino1 != pvm_dino:
            new_run.dino1.delete()
        if new_run.dino2 and new_run.dino2 != pvm_dino:
            new_run.dino2.delete()
        if new_run.dino3 and new_run.dino3 != pvm_dino:
            new_run.dino3.delete()
        
        # Get dinos for the next selection that haven't been selected yet
        selected_dino_ids = [d['id'] for d in selected_dinos]
        all_dinos = list(DWDino.objects.exclude(id__in=selected_dino_ids))
        random_dinos = get_random_dinos(all_dinos, new_run)
            
        # Return the next set of dinos to choose from
        return JsonResponse({
            'success': True,
            'selection_step': new_run.state,
            'selected_dinos': selected_dinos,
            'random_dinos': [{
                'id': dino.dino.id,
                'name': dino.dino.name,
                'hp': dino.hp,
                'atk': dino.atk,
                'defense': dino.defense,
                'spd': dino.spd,
                'crit': dino.crit,
                'crit_dmg': dino.crit_dmg,
                'attack': dino.attack.spe_effect,
            } for dino in random_dinos]
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
def set_next_fight_dinos(run, life=None):
    dinos = DWPvmNextFightDino.objects.filter(run=run)
    if dinos.exists():
        for dino in dinos:
            dino.delete()

    if run.level < 4:
        lvl_mult = 0.7 + 0.1 * run.level
        lvl_add = -0.3 + 0.1 * run.level
    elif run.level < 10:
        lvl_mult = 1.1 + 0.05 * (run.level - 4)
        lvl_add = 0.1 + 0.05 * (run.level - 4)
    elif run.level < 15:
        lvl_mult = 1.45 + 0.05 * (run.level - 10)
        lvl_add = 0.45 + 0.05 * (run.level - 10)
    elif run.level < 20:
        lvl_mult = 1.75 + 0.1 * (run.level - 15)
        lvl_add = 0.75 + 0.1 * (run.level - 15)
    else:
        lvl_mult = 2.3 + 0.1 * (run.level - 20)
        lvl_add = 1.3 + 0.1 * (run.level - 20)

    dw_user = DWUser.objects.get(user=run.user)

    seed = get_daily_seed(purpose=f"enemy_dino_select", run_number=dw_user.pvm_runs_td, run_lvl=run.level, additional=life)
    rand = random.Random(seed)
    all_dinos = list(DWDino.objects.all())
    random_dinos = rand.sample(all_dinos, 3)
    terrain = run.terrain
    if terrain.name == "Distorsion Spatio-Temporelle":
        ids, rearanged_stats = distorsion_terrain()
        for i, dino in enumerate(random_dinos):
            index = ids.index(dino.id)
            DWPvmNextFightDino.objects.create(
                run=run,
                dino=dino,
                hp=int(rearanged_stats['base_hp'][index] * lvl_mult),
                atk=int(rearanged_stats['base_atk'][index] * lvl_mult),
                defense=int(rearanged_stats['base_def'][index] * lvl_mult),
                spd=round(rearanged_stats['base_spd'][index] + lvl_add, 2),
                crit=round(rearanged_stats['base_crit'][index] + lvl_add*0.4, 2),
                crit_dmg=round(rearanged_stats['base_crit_dmg'][index] + lvl_add, 2),
                attack=dino.attack,
            )
    else:
        for i, dino in enumerate(random_dinos):
            # Apply terrain stat modifications
            base_stats = {
                'hp': int(dino.base_hp * lvl_mult),
                'atk': int(dino.base_atk * lvl_mult),
                'defense': int(dino.base_def * lvl_mult),
                'spd': round(1.0 + lvl_add, 2) if terrain.name == "Ere Glaciaire" else round(dino.base_spd + lvl_add, 2),
                'crit': round(dino.base_crit + lvl_add*0.4, 2),
                'crit_dmg': round(dino.base_crit_dmg + lvl_add, 2)
            }
            
            DWPvmNextFightDino.objects.create(
                run=run,
                dino=dino,
                hp=base_stats['hp'],
                atk=base_stats['atk'],
                defense=base_stats['defense'],
                spd=base_stats['spd'],
                crit=base_stats['crit'],
                crit_dmg=base_stats['crit_dmg'],
                attack=dino.attack,
            )
    
    return random_dinos

def set_next_abilities(run):
    abilities = DWPvmNextAbility.objects.filter(run=run)
    if abilities.exists():
        for ability in abilities:
            ability.delete()

    dw_user = DWUser.objects.get(user=run.user)
    dw_run = DWPvmRun.objects.get(user=run.user)
    seen_abilities = json.loads(dw_run.seen_abilities)

    seed = get_daily_seed(purpose=f"ability_select", run_number=dw_user.pvm_runs_td, run_lvl=run.level)
    rand = random.Random(seed)
    all_abilities = list(DWPvmAbility.objects.exclude(id__in=seen_abilities))
    random_abilities = rand.sample(all_abilities, 2)
    for ability in random_abilities:
        DWPvmNextAbility.objects.create(
            run=run,
            ability=ability,
        )
        seen_abilities.append(ability.id)
    dw_run.seen_abilities = json.dumps(seen_abilities)
    dw_run.save()

    return random_abilities

def calculate_total_stats(dino):
    """Calculate total stats including all abilities bonuses"""
    base_stats = {
        'hp': dino.hp,
        'atk': dino.atk,
        'defense': dino.defense,
        'spd': dino.spd,
        'crit': dino.crit,
        'crit_dmg': dino.crit_dmg
    }
    
    total_stats = base_stats.copy()
    # Get all abilities for the dino
    try :
        abilities = DWPvmRunAbility.objects.filter(dino=dino).select_related('ability')
        for ability in abilities:
            if ability.ability.name == "Boost de vie":
                total_stats['hp'] += int(total_stats['hp'] * 0.2)
            elif ability.ability.name == "Boost d'attaque":
                total_stats['atk'] += int(total_stats['atk'] * 0.2)
            elif ability.ability.name == "Boost de défense":
                total_stats['defense'] += int(total_stats['defense'] * 0.2)
            elif ability.ability.name == "Boost de vitesse":
                total_stats['spd'] += total_stats['spd'] * 0.2
                total_stats['spd'] = round(total_stats['spd'], 2)
            elif ability.ability.name == "Boost de % critique":
                total_stats['crit'] += 0.1
                total_stats['crit'] = round(total_stats['crit'], 2)
            elif ability.ability.name == "Boost de dégâts critiques":
                total_stats['crit_dmg'] += total_stats['crit_dmg'] * 0.3  
                total_stats['crit_dmg'] = round(total_stats['crit_dmg'], 2)
    except:
        pass
    
    return total_stats

@login_required
def get_run_fights_view(request):
    """View function to get all fights for the current PVM run."""
    try:
        # Get current run info
        run_info = get_object_or_404(DWPvmRun, user=request.user)
        
        # Get all PVM fights for this user since the run started
        fights = DWFight.objects.filter(
            user1=str(request.user),
            gamemode='pvm',
            date__gte=run_info.run_date
        ).order_by('-date')
        
        # Prepare fight data for the popup
        fights_data = []
        for fight in fights:
            fights_data.append({
                'id': fight.id,
                'date': fight.date.strftime('%d/%m/%Y %H:%M'),
                'user1_team': fight.user1_team,
                'user2_team': fight.user2_team,
                'winner': fight.winner,
                'is_victory': fight.winner == str(request.user)
            })
        
        return JsonResponse({
            'success': True,
            'fights': fights_data,
            'run_level': run_info.level
        })
        
    except DWPvmRun.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Aucune run active trouvée'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@require_POST
def start_battle_pvm(request):
    try:
        # Fetch the run info and dino details
        run_info = get_object_or_404(DWPvmRun, user=request.user)
        terrain = run_info.terrain

        user_dinos = []
        enemy_dinos = []
        for dino in [run_info.dino1, run_info.dino2, run_info.dino3]:
            dino_stats = calculate_total_stats(dino)
            user_dinos.append(load_dino_from_model(dino, dino_stats, 1, terrain.name))
        
        # Enemy dino details
        next_fight_dinos = DWPvmNextFightDino.objects.filter(run=run_info).select_related('dino')
        enemy_dino1 = next_fight_dinos[0] if len(next_fight_dinos) > 0 else None
        enemy_dino2 = next_fight_dinos[1] if len(next_fight_dinos) > 1 else None
        enemy_dino3 = next_fight_dinos[2] if len(next_fight_dinos) > 2 else None
        for dino in [enemy_dino1, enemy_dino2, enemy_dino3]:
            if dino:
                dino_stats = calculate_total_stats(dino)
                enemy_dinos.append(load_dino_from_model(dino, dino_stats, 2, terrain.name))
        
        team1_name = "team_joueur"
        team2_name = "team_ennemie"
        
        # Start battle simulation
        battle = GameState(
            (team1_name, user_dinos),
            (team2_name, enemy_dinos),
            terrain=terrain.name,
            run_id=run_info.id
        )
        battle_log = battle.run()
        winner = battle.get_winner()

        # Save fight result
        fight = DWFight.objects.create(
            user1=str(request.user),
            user2='Pvm_Enemy',
            user1_team=f"{run_info.dino1.dino.name} - {run_info.dino2.dino.name} - {run_info.dino3.dino.name}",
            user2_team=f"{enemy_dino1.dino.name} - {enemy_dino2.dino.name} - {enemy_dino3.dino.name}",
            winner=str(request.user) if winner == team1_name else 'Pvm_Enemy',
            gamemode="pvm",
            logs=battle_log
        )
        winner = 'Pvm_Enemy'

        # Update run info
        if winner == team1_name:
            run_info.stat_points += reward(run_info.level) if run_info.level <= 20 else reward(run_info.level)/2
            run_info.level += 1
            run_info.save()
            set_next_fight_dinos(run_info)
            if run_info.level % 2 == 0 and run_info.level <= 20:
                set_next_abilities(run_info)
            else:
                DWPvmNextAbility.objects.filter(run=run_info).delete()

            return JsonResponse({
                'success': True,
                'fight_id': fight.id,
                'winner': winner,
            })

        else:
            run_info.life -= 0
            run_info.save()
            if run_info.life <= 0:
                # Save to leaderboard before deleting the run
                terrain = run_info.terrain
                
                # Collect team dinos stats
                team_dinos_stats = []
                for dino in [run_info.dino1, run_info.dino2, run_info.dino3]:
                    if dino:
                        team_dinos_stats.append({
                            'name': dino.dino.name,
                            'hp': dino.hp,
                            'atk': dino.atk,
                            'defense': dino.defense,
                            'spd': dino.spd,
                            'crit': dino.crit,
                            'crit_dmg': dino.crit_dmg,
                            'hp_lvl': dino.hp_lvl,
                            'atk_lvl': dino.atk_lvl,
                            'defense_lvl': dino.defense_lvl,
                            'spd_lvl': dino.spd_lvl,
                            'crit_lvl': dino.crit_lvl,
                            'crit_dmg_lvl': dino.crit_dmg_lvl,
                        })
                
                # Collect abilities list
                abilities_list = []
                run_abilities = DWPvmRunAbility.objects.filter(run=run_info).select_related('ability', 'dino')
                for run_ability in run_abilities:
                    abilities_list.append({
                        'name': run_ability.ability.name,
                        'dino_name': run_ability.dino.dino.name if run_ability.dino else None,
                    })
                
                # Save to leaderboard
                DWPvmLeaderboard.objects.create(
                    user=request.user,
                    terrain=terrain,
                    run_level=run_info.level,
                    team_dinos_stats=team_dinos_stats,
                    abilities_list=abilities_list
                )
                
                DWPvmDino.objects.filter(user=request.user).delete()
                run_info.delete()
                dw_user = DWUser.objects.get(user=request.user)
                dw_user.pvm_runs_td += 1
                dw_user.save()
                return JsonResponse({
                    'success': False, 
                    'redirect': '/dinowars/pvm/', 
                    'fight_id': fight.id,
                    'winner': winner,
                })
            else:
                set_next_fight_dinos(run_info, run_info.life)
                return JsonResponse({
                    'success': False, 
                    'message': 'Vous avez perdu!', 
                    'fight_id': fight.id,
                    'winner': winner,
                })

    except Exception as e:
        print(f"Error in start_battle_pvm: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def leaderboard_view(request):
    """View function to display the PVM leaderboard."""
    try:
        # Get filter parameters
        user_filter = request.GET.get('user', '')
        terrain_filter = request.GET.get('terrain', '')
        
        # Base queryset - top 10 runs ordered by level and date
        queryset = DWPvmLeaderboard.objects.select_related('user', 'terrain')
        
        # Apply filters
        if user_filter:
            queryset = queryset.filter(user__username__icontains=user_filter)
        if terrain_filter:
            queryset = queryset.filter(terrain__name__icontains=terrain_filter)
        
        # Get top 10 results
        leaderboard_entries = queryset[:10]
        
        # Get all terrains for filter dropdown
        terrains = DWPvmTerrain.objects.all()
        
        context = {
            'leaderboard_entries': leaderboard_entries,
            'terrains': terrains,
            'user_filter': user_filter,
            'terrain_filter': terrain_filter,
        }
        
        return render(request, 'Blog/dinowars/leaderboard.html', context)
        
    except Exception as e:
        print(f"Error in leaderboard_view: {e}")
        return render(request, 'Blog/dinowars/leaderboard.html', {
            'leaderboard_entries': [],
            'terrains': [],
            'error': str(e)
        })
