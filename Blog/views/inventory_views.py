from django.shortcuts import render
from ..models import UserInventory, Item, Skin, Box
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required

@login_required
def user_inventory_view(request):
    # Récupérer l'inventaire de l'utilisateur connecté
    user_inventory = UserInventory.objects.filter(user=request.user).order_by('obtained_date')  # Trier par date d'obtention
    
    items = []
    
    # Récupérer les informations pour chaque item d'inventaire
    for inventory in user_inventory:
        item = inventory.item
        
        # Si l'item est un box
        if item.type == 'box':
            box = Box.objects.get(id=item.item_id)
            items.append({
                'type': 'box',
                'item_id': item.item_id,
                'name': box.name,
                'image': box.image.url,
                'open_price': box.open_price,
                'status': inventory.status,
                'obtained_date': inventory.obtained_date
            })
        # Si l'item est un skin
        elif item.type == 'skin':
            skin = Skin.objects.get(id=item.item_id)
            items.append({
                'type': 'skin',
                'item_id': item.item_id,
                'name': skin.name,
                'image': skin.image.url,
                'pattern': item.pattern,
                'status': inventory.status,
                'obtained_date': inventory.obtained_date,
                'skin_type': skin.type,
            })
    
    context = {
        'items': items
    }
    
    return render(request, 'Blog/inventory/inventory.html', context)

@login_required
def toggle_item_status(request):
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return HttpResponseBadRequest('<h1>400 Bad Request</h1><p>Requête non autorisée.</p>')
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        new_status = request.POST.get('status')

        # Trouver l'item dans l'inventaire de l'utilisateur connecté
        try:
            inventory_item = UserInventory.objects.get(id=item_id, user=request.user)
            inventory_item.status = new_status
            inventory_item.save()
            return JsonResponse({'success': True, 'message': 'Statut mis à jour avec succès.'})
        except UserInventory.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Item non trouvé.'})

    return JsonResponse({'success': False, 'message': 'Requête invalide.'})