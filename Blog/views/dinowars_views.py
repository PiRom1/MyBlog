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