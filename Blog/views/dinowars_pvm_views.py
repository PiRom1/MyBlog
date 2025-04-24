from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from Blog.models import DWUserDino, DWUserTeam, DWUser, DWPvmRun, DWPvmRunAbility, DWPvmDino, DWPvmNextFightDino, DWPvmNextAbility, DWDino, DWPvmNewRun
import json
import random
from django.views.decorators.http import require_POST
from django.db import transaction

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
        }
        return render(request, 'Blog/dinowars/pvm.html', context)

@login_required
def run_dino_details_view(request, dino_id):
    """View function to display details of a run dino."""
    try:        
        enemy = request.headers['enemy'] == 'true'
        if enemy:
            # Fetch the enemy dino details
            dino = get_object_or_404(DWPvmNextFightDino, id=dino_id, run__user=request.user)
            hp_lvl = int(((dino.hp - dino.dino.base_hp) / dino.dino.base_hp) * 10) + 1
            atk_lvl = int(((dino.atk - dino.dino.base_atk) / dino.dino.base_atk) * 10) + 1
            defense_lvl = int(((dino.defense - dino.dino.base_def) / dino.dino.base_def) * 10) + 1
            spd_lvl = int((dino.spd - dino.dino.base_spd) * 10) + 1
            crit_lvl = int((dino.crit - dino.dino.base_crit) * 25) + 1
            crit_dmg_lvl = int((dino.crit_dmg - dino.dino.base_crit_dmg) * 10) + 1
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
        
        # Get run info for stat points display
        try:
            run_info = DWPvmRun.objects.get(user=request.user)
        except DWPvmRun.DoesNotExist:
            run_info = None
        
        # Render the template with the dino details
        return render(request, 'Blog/dinowars/_dino_details_popup_pvm.html', {
            'dino': dino,
            'stats': stats,
            'enemy': enemy,
            'run_info': run_info,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def fib(i):
    if i == 1 : return 5
    if i == 2 : return 8
    return fib(i-1) + fib(i-2)

def sumfib(i):
    return sum(fib(j) for j in range(1, i+1))

def stat_cost(i):
    return int(sumfib(i)/6)+1

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
            dino.hp_lvl += 1
            dino.hp += int(0.1*dino.hp)
        elif stat_name == 'atk':
            dino.atk_lvl += 1
            dino.atk += int(0.1*dino.atk) 
        elif stat_name == 'defense':
            dino.defense_lvl += 1
            dino.defense += int(0.1*dino.defense)
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
    new_run.dino1 = DWPvmDino.objects.create(
        user=new_run.user,
        dino=random_dinos[0],
        hp=random_dinos[0].base_hp,
        atk=random_dinos[0].base_atk,
        defense=random_dinos[0].base_def,
        spd=random_dinos[0].base_spd,
        crit=random_dinos[0].base_crit,
        crit_dmg=random_dinos[0].base_crit_dmg,
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
        hp=random_dinos[1].base_hp,
        atk=random_dinos[1].base_atk,
        defense=random_dinos[1].base_def,
        spd=random_dinos[1].base_spd,
        crit=random_dinos[1].base_crit,
        crit_dmg=random_dinos[1].base_crit_dmg,
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
        hp=random_dinos[2].base_hp,
        atk=random_dinos[2].base_atk,
        defense=random_dinos[2].base_def,
        spd=random_dinos[2].base_spd,
        crit=random_dinos[2].base_crit,
        crit_dmg=random_dinos[2].base_crit_dmg,
        hp_lvl=1,
        atk_lvl=1,
        defense_lvl=1,
        spd_lvl=1,
        crit_lvl=1,
        crit_dmg_lvl=1,
        attack=random_dinos[2].attack
    )
    new_run.save()
    return new_run

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
            if new_run.state < 4:  # Selection not completed
                random_dinos = [new_run.dino1.dino, new_run.dino2.dino, new_run.dino3.dino]
                selected_dinos = [dino.dino for dino in [existing_run.dino1, existing_run.dino2, existing_run.dino3] if dino is not None]
                print(selected_dinos)
                context = {
                    'random_dinos': random_dinos,
                    'selection_step': new_run.state,
                    'selected_dinos': selected_dinos
                }
                return render(request, 'Blog/dinowars/new_run.html', context)
        except (DWPvmRun.DoesNotExist, DWPvmNewRun.DoesNotExist) as e:
            pass
    
    # Create a new DWPvmNewRun object for this user
    DWPvmNewRun.objects.filter(user=request.user).delete()  # Clear any existing entries
    new_run = DWPvmNewRun.objects.create(user=request.user, state=1)
    final_run = DWPvmRun.objects.create(user=request.user)
    
    # Get three random dinos for initial selection
    all_dinos = list(DWDino.objects.all())
    if len(all_dinos) < 3:
        return JsonResponse({'error': 'Not enough dinos in database.'}, status=500)
    
    random_dinos = random.sample(all_dinos, 3)
    set_new_run_dinos(new_run, random_dinos)
    
    context = {
        'random_dinos': random_dinos,
        'selection_step': 1,
        'selected_dinos': []
    }
    return render(request, 'Blog/dinowars/new_run.html', context)

@login_required
@require_POST
def select_run_dino_view(request):
    """Handle the dino selection process for a new run."""
    try:
        data = json.loads(request.body)
        dino_id = data.get('dino_id')
        
        # Retrieve or create the DWPvmNewRun object
        try:
            new_run = DWPvmNewRun.objects.get(user=request.user)
            final_run = DWPvmRun.objects.get(user=request.user)
        except DWPvmRun.DoesNotExist:
            final_run = DWPvmRun.objects.create(user=request.user)
        except DWPvmNewRun.DoesNotExist:
            new_run = DWPvmNewRun.objects.create(user=request.user, state=1)
        
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
        if len(all_dinos) < 3:
            random_dinos = all_dinos
        else:
            random_dinos = random.sample(all_dinos, 3)

        set_new_run_dinos(new_run, random_dinos)
            
        # Return the next set of dinos to choose from
        return JsonResponse({
            'success': True,
            'selection_step': new_run.state,
            'selected_dinos': selected_dinos,
            'random_dinos': [{
                'id': dino.id,
                'name': dino.name,
                'hp': dino.base_hp,
                'atk': dino.base_atk,
                'defense': dino.base_def,
                'spd': dino.base_spd,
                'crit': dino.base_crit,
                'crit_dmg': dino.base_crit_dmg,
                'attack': dino.attack.spe_effect,
            } for dino in random_dinos]
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)