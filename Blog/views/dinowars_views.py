import math
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from Blog.models import DWUserDino, DWUserTeam, DWUser, DWFight, DWDinoItem, Skin, UserInventory, Item
from django.http import JsonResponse
import json
from django.views.decorators.http import require_POST
import random
from ..models import DWArena, DWDino, DWUserDino, DWUser, User
from django.utils import timezone
from datetime import datetime
from Blog.utils.dw_battle_logic import load_dino_from_model, GameState
from Blog.views.quests_views import validate_objective_quest


@login_required
def user_dinos_view(request):
    # Get all dinos owned by user and sort them by level, then by name
    user_dinos = DWUserDino.objects.filter(user=request.user).select_related('dino').order_by('-level', 'dino__name')
    
    # Get equipped runes for all dinos
    for dino in user_dinos:
        equipped_items = DWDinoItem.objects.filter(dino=dino).select_related('item')
        dino.equipped_runes = {
            item.slot: item.item
            for item in equipped_items
        }
        dino.equipped_runes_rarity = {
            item.slot: Skin.objects.get(id=item.item.item_id).rarity.name
            for item in equipped_items
        }
    
    # Get user's team if exists
    try:
        user_team = DWUserTeam.objects.filter(user=request.user)
    except DWUserTeam.DoesNotExist:
        user_team = None
        
    # Get user stats
    try:
        user_stats = DWUser.objects.get(user=request.user)
    except DWUser.DoesNotExist:
        user_stats = None
    
    context = {
        'user_dinos': user_dinos,
        'user_team': user_team,
        'user_stats': user_stats
    }
    return render(request, 'Blog/dinowars/user_dinos.html', context)

@login_required
def edit_team_view(request, team_id=None):
    user_dinos = DWUserDino.objects.filter(user=request.user)
    
    # Get specific team if team_id is provided, otherwise get first team
    if team_id:
        current_team = DWUserTeam.objects.filter(id=team_id, user=request.user).first()
        if not current_team:
            return JsonResponse({'success': False, 'error': 'Team not found'})
    else:
        current_team = None
    
    if request.method == 'POST':
        try:
            team_name = request.POST.get('team_name')
            dino1_id = request.POST.get('dino1')
            dino2_id = request.POST.get('dino2')
            dino3_id = request.POST.get('dino3')
            
            if not team_name:
                raise ValueError("Team name is required")
            
            # Verify all dinos belong to user
            dino1 = user_dinos.get(id=dino1_id)
            dino2 = user_dinos.get(id=dino2_id)
            dino3 = user_dinos.get(id=dino3_id)
            
            # Check if dinos are unique
            if len({dino1.dino.name, dino2.dino.name, dino3.dino.name}) != 3:
                raise ValueError("All dinosaurs in the team must be different")
            
            if current_team:
                current_team.name = team_name
                current_team.dino1 = dino1
                current_team.dino2 = dino2
                current_team.dino3 = dino3
                current_team.save()
            else:
                current_team = DWUserTeam.objects.create(
                    user=request.user,
                    name=team_name,
                    dino1=dino1,
                    dino2=dino2,
                    dino3=dino3
                )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'team': {
                        'id': current_team.id,
                        'name': current_team.name,
                        'dino1': {'name': dino1.dino.name, 'level': dino1.level},
                        'dino2': {'name': dino2.dino.name, 'level': dino2.level},
                        'dino3': {'name': dino3.dino.name, 'level': dino3.level},
                    }
                })
            return redirect('user_dinos_view')
            
        except (DWUserDino.DoesNotExist, ValueError) as e:
            error_message = str(e) if isinstance(e, ValueError) else "Invalid dino selection"
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': error_message})
            return render(request, 'Blog/dinowars/_edit_team_popup.html', {
                'user_dinos': user_dinos,
                'current_team': current_team,
                'error': error_message
            })
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'Blog/dinowars/_edit_team_popup.html', {
            'user_dinos': user_dinos,
            'current_team': current_team
        })
    return render(request, 'Blog/dinowars/_edit_team_popup.html', {
        'user_dinos': user_dinos,
        'current_team': current_team
    })

@login_required
def delete_team_view(request, team_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
        
    try:
        team = DWUserTeam.objects.get(id=team_id, user=request.user)
        team.delete()
        return JsonResponse({'success': True})
    except DWUserTeam.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Team not found or access denied'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
def get_item_bonus(item, slot_type, slot_number):
    rarity = Skin.objects.get(id=item.item_id).rarity.name
    if item is None:
        return 
    if slot_type in ['hp', 'atk', 'defense']:
        if rarity == 'common':
            bonus = 0.1 * slot_number
        elif rarity == 'uncommon':
            bonus = 0.2 * slot_number
        elif rarity == 'rare':
            bonus = 0.3 * slot_number
        elif rarity == 'legendary':
            bonus = 0.4 * slot_number
        bonus = int(bonus)
    else:
        if rarity == 'common':
            bonus = 0.1
        elif rarity == 'uncommon':
            bonus = 0.2
        elif rarity == 'rare':
            bonus = 0.3
        elif rarity == 'legendary':
            bonus = 0.4
        if slot_type == 'crit':
            bonus = round(bonus*0.4, 2)
    return bonus

def calculate_total_stats(dino):
    """Calculate total stats including all rune bonuses"""
    base_stats = {
        'hp': dino.hp,
        'atk': dino.atk,
        'defense': dino.defense,
        'spd': dino.spd,
        'crit': dino.crit,
        'crit_dmg': dino.crit_dmg
    }
    
    total_stats = base_stats.copy()
    
    # Get all equipped runes
    equipped_items = DWDinoItem.objects.filter(dino=dino).select_related('item')
    
    # Calculate bonuses from each rune
    for item in equipped_items:
        bonus = get_item_bonus(item.item, item.slot, base_stats[item.slot])
        if bonus:
            if item.slot in ['spd', 'crit', 'crit_dmg']:
                total_stats[item.slot] = round(total_stats[item.slot] + bonus, 2)
            else:
                total_stats[item.slot] += bonus
    
    return total_stats

@login_required
def dino_details_view(request, dino_id):
    try:
        dino = DWUserDino.objects.get(id=dino_id, user=request.user)
        
        # Check for fusion candidates (same name and level)
        fusion_candidates = DWUserDino.objects.filter(
            user=request.user,
            dino=dino.dino,
            level=dino.level
        ).exclude(id=dino.id).exists()
        
        # Get equipped items for display
        equipped_items = DWDinoItem.objects.filter(dino=dino).select_related('item')
        
        # Calculate individual bonuses for display
        stats = {
            'hp': {'base': dino.hp, 'bonus': 0},
            'atk': {'base': dino.atk, 'bonus': 0},
            'defense': {'base': dino.defense, 'bonus': 0},
            'spd': {'base': dino.spd, 'bonus': 0},
            'crit': {'base': dino.crit, 'bonus': 0},
            'crit_dmg': {'base': dino.crit_dmg, 'bonus': 0}
        }
        
        # Calculate individual bonuses
        for item in equipped_items:
            bonus = get_item_bonus(item.item, item.slot, stats[item.slot]['base'])
            if bonus:
                stats[item.slot]['bonus'] = bonus
        
        # Get total stats
        total_stats = calculate_total_stats(dino)
        
        # Add total values to stats dictionary
        for stat, value in total_stats.items():
            stats[stat]['total'] = value
        
        return render(request, 'Blog/dinowars/_dino_details_popup.html', {
            'dino': dino,
            'stats': stats,
            'has_fusion_candidates': fusion_candidates
        })
    except DWUserDino.DoesNotExist:
        return JsonResponse({'error': 'Dino not found'}, status=404)

@login_required
def dino_runes_view(request, dino_id):
    dino = get_object_or_404(DWUserDino, id=dino_id, user=request.user)
    
    # Get equipped runes
    equipped_runes = {
        item.slot: item 
        for item in DWDinoItem.objects.filter(dino=dino).select_related('item')
    }
    
    # Get base stats and total stats
    base_stats = {
        'hp': dino.hp, 'atk': dino.atk, 'defense': dino.defense,
        'spd': dino.spd, 'crit': dino.crit, 'crit_dmg': dino.crit_dmg
    }
    total_stats = calculate_total_stats(dino)
    
    # Calculate stats for each slot
    slots_data = []
    for slot_type, slot_name in DWDinoItem.SLOT_TYPES:
        base = base_stats[slot_type]
        bonus = 0
        rarity = None
        skin_name = None
        
        if slot_type in equipped_runes:
            item = equipped_runes[slot_type].item
            skin = Skin.objects.get(id=item.item_id)
            bonus = get_item_bonus(item, slot_type, base)
            rarity = skin.rarity.name
            skin_name = skin.name
            
        slots_data.append({
            'type': slot_type,
            'name': slot_name,
            'base': base,
            'bonus': bonus,
            'total': total_stats[slot_type],
            'rarity': rarity,
            'skin_name': skin_name
        })
    
    context = {
        'dino': dino,
        'slots': slots_data,
    }
    
    return render(request, 'Blog/dinowars/_runes_popup.html', context)

@login_required
def runes_inventory_view(request):
    # Get all runes/items from user's inventory that aren't equipped nor marked as favorite
    equipped_item_ids = DWDinoItem.objects.filter(dino__user=request.user).values_list('item_id', flat=True)
    inventory_items = UserInventory.objects.filter(
        user=request.user,
        item__type='skin',
        favorite=False 
    ).exclude(
        item__id__in=equipped_item_ids
    ).select_related('item')
    
    # Define rarity order
    rarity_order = {
        'legendary': 0,
        'rare': 1,
        'uncommon': 2,
        'common': 3
    }
    
    # Create items data with rarity for sorting
    items_data = [{
        'id': item.item.id,
        'name': Skin.objects.get(id=item.item.item_id).name,
        'rarity': Skin.objects.get(id=item.item.item_id).rarity.name,
    } for item in inventory_items]
    
    # Sort items by rarity according to the defined order
    items_data.sort(key=lambda x: rarity_order.get(x['rarity'], 999))
    
    return JsonResponse({'items': items_data})

@login_required
def equip_rune(request, dino_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
        
    try:
        data = json.loads(request.body)
        slot = data.get('slot')
        remove = data.get('remove', False)
        
        # Validate dino ownership
        dino = get_object_or_404(DWUserDino, id=dino_id, user=request.user)
        
        # Get base stat value for bonus calculation
        slot_stats = {'hp': dino.hp, 'atk': dino.atk, 'defense': dino.defense, 
                     'spd': dino.spd, 'crit': dino.crit, 'crit_dmg': dino.crit_dmg}
        base_stat = slot_stats[slot]
        
        # Remove any existing rune in this slot
        DWDinoItem.objects.filter(dino=dino, slot=slot).delete()
        bonus = 0
        skin = None
        
        if not remove:
            item_id = data.get('item_id')
            # Validate item ownership
            item = get_object_or_404(Item, id=item_id)
            user_item = get_object_or_404(UserInventory, user=request.user, item=item)
            
            # Equip new rune
            dino_item = DWDinoItem.objects.create(
                dino=dino,
                slot=slot,
                item=item
            )
            
            # Calculate bonus
            skin = Skin.objects.get(id=item.item_id)
            bonus = get_item_bonus(item, slot, base_stat)
        
        # Calculate total stats after equipment change
        total_stats = calculate_total_stats(dino)
        
        return JsonResponse({
            'success': True,
            'bonus': bonus,
            'base_stat': base_stat,
            'total_stat': total_stats[slot],
            'skin_name': skin.name if skin else None,
            'skin_rarity': skin.rarity.name if skin else None,
            'icon_type': 'ss' if not remove else 'rs',
        })
        
    except (json.JSONDecodeError, KeyError) as e:
        return JsonResponse({'success': False, 'error': 'Invalid request data'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def fuse_dinos(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        data = json.loads(request.body)
        dino_id1 = data.get('dino_id1')
        dino_id2 = data.get('dino_id2')
        
        # Get both dinos and verify ownership and compatibility
        dino1 = get_object_or_404(DWUserDino, id=dino_id1, user=request.user)
        dino2 = get_object_or_404(DWUserDino, id=dino_id2, user=request.user)
        
        if dino1.dino.name != dino2.dino.name:
            raise ValueError("Dinos must be of the same type")
        
        if dino1.level != dino2.level:
            raise ValueError("Dinos must be of the same level")
        
        # Create new dino with level + 1
        new_dino = DWUserDino.objects.create(
            user=request.user,
            dino=dino1.dino,
            level=dino1.level + 1,
            hp=int(dino1.hp * 1.1),
            atk=int(dino1.atk * 1.1),
            defense=int(dino1.defense * 1.1),
            spd=round(dino1.spd + 0.1, 2),
            crit=round(dino1.crit + 0.04, 2),
            crit_dmg=round(dino1.crit_dmg + 0.1, 2),
            attack=dino1.attack,
        )
        
        # Delete old dinos
        dino1.delete()
        dino2.delete()
        
        return JsonResponse({
            'success': True,
            'new_dino_id': new_dino.id
        })
        
    except (json.JSONDecodeError, ValueError) as e:
        return JsonResponse({'success': False, 'error': str(e)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': 'An error occurred during fusion'})

@require_POST
def hatch_dino(request):
    try:
        dw_user = DWUser.objects.get(user=request.user)
        user = request.user

        if dw_user.free_hatch <= 0 and user.coins < 30:
            return JsonResponse({
                'success': False,
                'error': 'Vous n\'avez pas assez de pièces pour faire éclore un œuf.'
            })

        # Deduct cost if not free
        if dw_user.free_hatch <= 0:
            user.coins -= 30
            user.save()
        else:
            dw_user.free_hatch -= 1
            dw_user.save()

        # Get random dino from available ones
        available_dinos = DWDino.objects.all()
        random_dino = random.choice(available_dinos)

        # Create new user dino at level 1
        new_dino = DWUserDino.objects.create(
            user=user,
            dino=random_dino,
            level=1,
            hp=random_dino.base_hp,
            atk=random_dino.base_atk,
            defense=random_dino.base_def,
            spd=random_dino.base_spd,
            crit=random_dino.base_crit,
            crit_dmg=random_dino.base_crit_dmg,
            attack=random_dino.attack,
        )

        return JsonResponse({
            'success': True,
            'dino_id': new_dino.id
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def battle_view(request):
    # Get user's teams
    user_teams = DWUserTeam.objects.filter(user=request.user, in_arena=False)
    
    # Get all players and their teams
    players_with_teams = []
    for user in User.objects.all():
        teams = DWUserTeam.objects.filter(user=user, in_arena=False)
        if teams.exists():
            players_with_teams.append({
                'username': user.username,
                'teams': teams
            })
    
    context = {
        'user_teams': user_teams,
        'players': players_with_teams,
    }
    
    return render(request, 'Blog/dinowars/_battle_popup.html', context)

@login_required
def arena_view(request):
    # Get user's teams
    user_teams = DWUserTeam.objects.filter(user=request.user)
    
    # Get Arena champion's team
    arena_team = DWUserTeam.objects.filter(in_arena=True).first()

    # Get current arena Info
    arena_info = DWArena.objects.last()
    
    # Calculate time difference
    if arena_info:
        now = timezone.now()
        delta = now - arena_info.date
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        time_diff = {
            'days': days,
            'hours': hours,
            'minutes': minutes
        }
    else:
        time_diff = None

    arena_energy = DWUser.objects.get(user=request.user).arena_energy
    
    context = {
        'user_teams': user_teams,
        'arena_team': arena_team,
        'arena_info': arena_info,
        'arena_energy': arena_energy,
        'time_diff': time_diff
    }
    
    return render(request, 'Blog/dinowars/_arena_popup.html', context)

@login_required
@require_POST
def start_battle(request):
        data = json.loads(request.body)
        attacker_team_id = data.get('attacker_team_id')
        defender_team_id = data.get('defender_team_id')
        gamemode = data.get('gamemode', 'duel')  # Default to duel if not specified

        # Validate team ownership and existence
        attacker_team = get_object_or_404(DWUserTeam, id=attacker_team_id, user=request.user)
        defender_team = get_object_or_404(DWUserTeam, id=defender_team_id)

        # Check arena energy if gamemode is arena
        if (gamemode == 'arena'):
            validate_objective_quest(user = request.user, action = "dw_arena")

            user_stats = DWUser.objects.get(user=request.user)
            if user_stats.arena_energy <= 0:
                return JsonResponse({
                    'success': False,
                    'error': 'Not enough arena energy'
                })
            user_stats.arena_energy -= 1
            user_stats.save()

        # Load teams with their stats
        attacker_dinos = []
        for dino in [attacker_team.dino1, attacker_team.dino2, attacker_team.dino3]:
            dino_stats = calculate_total_stats(dino)
            attacker_dinos.append(load_dino_from_model(dino, dino_stats,1))

        defender_dinos = []
        for dino in [defender_team.dino1, defender_team.dino2, defender_team.dino3]:
            dino_stats = calculate_total_stats(dino)
            defender_dinos.append(load_dino_from_model(dino, dino_stats,2))

        team1_name = request.user.username+'_'+attacker_team.name
        team2_name = defender_team.user.username+'_'+defender_team.name

        # Start battle simulation
        battle = GameState(
            (team1_name, attacker_dinos),
            (team2_name, defender_dinos)
        )
        battle_log = battle.run()
        winner = battle.get_winner()

        # Save fight result
        fight = DWFight.objects.create(
            user1=str(request.user),
            user2=str(defender_team.user),
            user1_team=str(attacker_team),
            user2_team=str(defender_team),
            winner=str(request.user) if winner == team1_name else str(defender_team.user),
            gamemode=gamemode,
            logs=battle_log
        )

        attacker_user = DWUser.objects.get(user=request.user)
        defender_user = DWUser.objects.get(user=defender_team.user)

        # Handle arena specific logic
        if gamemode == 'arena':
            current_arena = DWArena.objects.filter(active=True).first()
            if winner == team1_name:
                # If attacker wins, make their team the new arena team
                if current_arena:
                    current_arena.active = False
                    current_arena.save()
                    
                # Create new arena entry
                DWArena.objects.create(
                    user=request.user,
                    team=attacker_team,
                )
                # Update team status
                defender_team.in_arena = False
                attacker_team.in_arena = True
                defender_team.save()
                attacker_team.save()
                # Update dinos' status
                for dino in attacker_team.dino1, attacker_team.dino2, attacker_team.dino3:
                    dino.in_arena = True
                    dino.save()
                for dino in defender_team.dino1, defender_team.dino2, defender_team.dino3:
                    dino.in_arena = False
                    dino.save()

                # Update elo and wins/losses
                eloDiff = attacker_user.elo - defender_user.elo
                if eloDiff >= 0:
                    elo = int(pow(math.e,-(pow(abs(eloDiff),1.6)/5000))*20+1)
                    attacker_user.elo += elo
                    defender_user.elo -= elo
                else:         
                    elo = 100 - int(pow(math.e,-(pow(abs(eloDiff),2)/100000))*80)
                    attacker_user.elo += elo
                    defender_user.elo -= elo                                                                              
                attacker_user.wins += 1
                defender_user.losses += 1
                attacker_user.save()
                defender_user.save()



            else:
                # If defender wins, increment their win streak
                if current_arena:
                    current_arena.win_streak += 1
                    current_arena.save()
                
                # Update elo and wins/losses
                eloDiff = defender_user.elo - attacker_user.elo
                if eloDiff >= 0:
                    elo = int(pow(math.e,-(pow(abs(eloDiff),1.6)/5000))*20+1)
                    attacker_user.elo -= elo
                    defender_user.elo += elo
                else:         
                    elo = 100 - int(pow(math.e,-(pow(abs(eloDiff),2)/100000))*80)
                    attacker_user.elo -= elo
                    defender_user.elo += elo                                                                              
                attacker_user.losses += 1
                defender_user.wins += 1
                attacker_user.save()
                defender_user.save()

        return JsonResponse({
            'success': True,
            'battle_log': json.loads(battle_log),
            'fight_id': fight.id,
            'winner': winner,
            'gamemode': gamemode
        })

    # except Exception as e:
    #     return JsonResponse({
    #         'success': False,
    #         'error': str(e)
    #     })

@login_required
def battle_analytics_view(request, fight_id):
    fight = get_object_or_404(DWFight, id=fight_id)
    logs = json.loads(fight.logs)
    
    # Extract initial and final states
    initial_state = next(log for log in logs if log['type'] == 'initial_state')
    final_state = next(log for log in logs if log['type'] == 'final_state')
    
    # Process battle events
    dino_hp_timeline = {}
    damage_dealt = {}
    crit_counts = {}
    effects_timeline = {}
    
    # Create mappings from ID to team and name to ID
    dino_id_to_team = {}
    dino_name_to_id = {}
    team_names = list(initial_state['initial_state'].keys())
    
    # Initialize HP timeline with initial values and create mappings
    for team_idx, team_name in enumerate(team_names):
        team = initial_state['initial_state'][team_name]
        for dino in team:
            dino_id = dino['id']
            dino_name = dino['name']
            
            # Create a unique display name that includes team info
            display_name = f"{dino_name} (Team {team_idx+1})"
            
            # Store mappings
            dino_id_to_team[dino_id] = team_name
            dino_name_to_id[display_name] = dino_id
            
            # Initialize HP timeline
            dino_hp_timeline[display_name] = [(0, dino['stats']['hp'])]  # Start at tick 0
    
    for log in logs:
        if log['type'] == 'attack':
            tick = log['tick']
            attacker_id = log['attacker_id']
            defender_id = log['defender_id']
            damage = log['damage']
            defender_hp = log['defender_hp']
            is_crit = log['is_crit']
            
            # Get display names from IDs
            attacker_team = dino_id_to_team[attacker_id]
            defender_team = dino_id_to_team[defender_id]
            attacker_display = f"{log['attacker']} (Team {team_names.index(attacker_team)+1})"
            defender_display = f"{log['defender']} (Team {team_names.index(defender_team)+1})"
            
            # Update HP timeline from attacks
            dino_hp_timeline[defender_display].append((tick, defender_hp))
            
            # Update damage dealt stats
            if attacker_display not in damage_dealt:
                damage_dealt[attacker_display] = {
                    'total': 0, 
                    'hits': 0, 
                    'crits': 0, 
                    'team': attacker_team,
                    'reflect_damage': 0,
                    'poison_damage': 0
                }
            damage_dealt[attacker_display]['total'] += damage
            damage_dealt[attacker_display]['hits'] += 1
            if is_crit:
                damage_dealt[attacker_display]['crits'] += 1
                
        elif log['type'] == 'effect':
            tick = log['tick']
            dino_id = log['dino_id']
            event = log['event']
            value = log['value']
            
            # Get display name from ID
            dino_team = dino_id_to_team[dino_id]
            dino_display = f"{log['dino']} (Team {team_names.index(dino_team)+1})"
            
            # Track effects for timeline display
            if dino_display not in effects_timeline:
                effects_timeline[dino_display] = []
            effects_timeline[dino_display].append((tick, event, value))
            
            # Update HP timeline if effect modifies HP
            if log['stat'] == 'hp':
                # Get the last known HP value
                last_hp = dino_hp_timeline[dino_display][-1][1]
                # Add new HP point after effect
                dino_hp_timeline[dino_display].append((tick, last_hp - log['value']))  # Subtract value since damage is positive
                
                # Track reflect and poison damage
                if event == 'reflect_damage' or event == 'poison_damage':
                    # Get the opposing team name
                    dino_team_idx = team_names.index(dino_team)
                    opposing_team_idx = 1 - dino_team_idx  # 0 becomes 1, 1 becomes 0
                    opposing_team = team_names[opposing_team_idx]
                    
                    # Find the appropriate source dino based on damage type
                    source_dino_name = "Stegosaurus" if event == "reflect_damage" else "Dilophosaurus"
                    source_found = False
                    
                    # Look for the source dino in the opposing team
                    for dino in initial_state['initial_state'][opposing_team]:
                        if dino['name'] == source_dino_name:
                            source_display = f"{source_dino_name} (Team {opposing_team_idx+1})"
                            source_found = True
                            break
                    
                    if source_found:
                        # Initialize if not exists
                        if source_display not in damage_dealt:
                            damage_dealt[source_display] = {
                                'total': 0, 
                                'hits': 0, 
                                'crits': 0, 
                                'team': opposing_team,
                                'reflect_damage': 0,
                                'poison_damage': 0
                            }
                            
                        # Add to appropriate damage type
                        if event == 'reflect_damage':
                            damage_dealt[source_display]['reflect_damage'] += value
                        elif event == 'poison_damage':
                            damage_dealt[source_display]['poison_damage'] += value

    # Initialize damage timeline
    dino_damage_timeline = {}
    for team_idx, team_name in enumerate(team_names):
        for dino in initial_state['initial_state'][team_name]:
            dino_name = dino['name']
            display_name = f"{dino_name} (Team {team_idx+1})"
            dino_damage_timeline[display_name] = [(0, 0)]  # Start at tick 0 with 0 damage
            
    # Process attacks to build damage timeline
    for log in logs:
        if log['type'] == 'attack':
            tick = log['tick']
            attacker_id = log['attacker_id']
            damage = log['damage']
            
            # Get display name from ID
            attacker_team = dino_id_to_team[attacker_id]
            attacker_display = f"{log['attacker']} (Team {team_names.index(attacker_team)+1})"
            
            # Add damage point to timeline
            last_damage = dino_damage_timeline[attacker_display][-1][1]
            dino_damage_timeline[attacker_display].append((tick, last_damage + damage))

    # Calculate KPIs
    fight_duration = final_state['tick']
    total_attacks = sum(stats['hits'] for stats in damage_dealt.values())
    total_damage = sum(stats['total'] for stats in damage_dealt.values())
    total_crits = sum(stats['crits'] for stats in damage_dealt.values())
    
    # Calculate team-specific KPIs
    team1_name = team_names[0]
    team2_name = team_names[1]
    
    team1_damage = sum(stats['total'] for _, stats in damage_dealt.items() if stats['team'] == team1_name)
    team1_hits = sum(stats['hits'] for _, stats in damage_dealt.items() if stats['team'] == team1_name)
    team1_crits = sum(stats['crits'] for _, stats in damage_dealt.items() if stats['team'] == team1_name)

    team2_damage = sum(stats['total'] for _, stats in damage_dealt.items() if stats['team'] == team2_name)
    team2_hits = sum(stats['hits'] for _, stats in damage_dealt.items() if stats['team'] == team2_name)
    team2_crits = sum(stats['crits'] for _, stats in damage_dealt.items() if stats['team'] == team2_name)

    kpis = {
        'duration': fight_duration / 100,  # Convert ticks to seconds
        'team1': {
            'name': team1_name,
            'total_attacks': team1_hits,
            'total_damage': team1_damage,
            'avg_damage_per_hit': team1_damage / team1_hits if team1_hits > 0 else 0,
            'crit_rate': (team1_crits / team1_hits * 100) if team1_hits > 0 else 0
        },
        'team2': {
            'name': team2_name,
            'total_attacks': team2_hits,
            'total_damage': team2_damage,
            'avg_damage_per_hit': team2_damage / team2_hits if team2_hits > 0 else 0,
            'crit_rate': (team2_crits / team2_hits * 100) if team2_hits > 0 else 0
        }
    }
    
    # Sort damage_dealt by team number first, then by dino name
    def get_sort_key(dino_display):
        # Extract team number and dino name from display name format "DinoName (Team X)"
        parts = dino_display.split(" (Team ")
        dino_name = parts[0]
        team_number = int(parts[1].rstrip(")"))
        return (team_number, dino_name)
    
    # Sort damage_dealt
    sorted_damage_dealt = dict(sorted(damage_dealt.items(), key=lambda x: get_sort_key(x[0])))
    
    # Sort effects_timeline
    sorted_effects_timeline = dict(sorted(effects_timeline.items(), key=lambda x: get_sort_key(x[0])))
    
    context = {
        'fight': fight,
        'dino_hp_timeline': json.dumps(dino_hp_timeline),
        'dino_damage_timeline': json.dumps(dino_damage_timeline),
        'damage_dealt': sorted_damage_dealt,
        'effects_timeline': sorted_effects_timeline,
        'kpis': kpis,
        'winner': final_state['winner']
    }
    
    return render(request, 'Blog/dinowars/battle_analytics.html', context)



def remove_runes(request):
    
    data = json.loads(request.body)

    if 'dino_id' not in data:
        return JsonResponse({'success' : False, 'error' : "Dino id not in data"})

    dino = DWUserDino.objects.get(id = data.get('dino_id'))
    runes = DWDinoItem.objects.filter(dino = dino)
    runes_id = list(runes.values_list('id', flat=True))
    runes.delete()

    return JsonResponse({'success' : True, 'runes_id' : runes_id})
