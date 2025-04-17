from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from Blog.models import DWUserDino, DWUserTeam, DWUser, DWPvmRun, DWPvmRunAbility, DWPvmDino, DWPvmNextFightDino, DWPvmNextAbility

@login_required
def pvm_view(request):
    # Get current run info if exists
    try:
        run_info = DWPvmRun.objects.get(user=request.user)
        run_abilities = DWPvmRunAbility.objects.filter(run=run_info).select_related('ability')
        run_dinos = [run_info.dino1, run_info.dino2, run_info.dino3]
        next_fight_dinos = DWPvmNextFightDino.objects.filter(run=run_info).select_related('dino')
        next_abilities = DWPvmNextAbility.objects.filter(run=run_info).select_related('ability')
    except DWPvmRun.DoesNotExist:
        run_info = None
        run_abilities = None
        run_dinos = None
        next_fight_dinos = None
        next_abilities = None
    
    context = {
        'run_info': run_info,
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
        else:
            # Fetch the user's dino details
            dino = get_object_or_404(DWPvmDino, id=dino_id, user=request.user)
        
        # Calculate stats for display
        stats = {
            'hp': {'base': dino.hp, 'bonus': 0, 'total': dino.hp},
            'atk': {'base': dino.atk, 'bonus': 0, 'total': dino.atk},
            'defense': {'base': dino.defense, 'bonus': 0, 'total': dino.defense},
            'spd': {'base': dino.spd, 'bonus': 0, 'total': dino.spd},
            'crit': {'base': dino.crit, 'bonus': 0, 'total': dino.crit},
            'crit_dmg': {'base': dino.crit_dmg, 'bonus': 0, 'total': dino.crit_dmg}
        }
        
        # Render the template with the dino details
        return render(request, 'Blog/dinowars/_dino_details_popup_pvm.html', {
            'dino': dino,
            'stats': stats
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
