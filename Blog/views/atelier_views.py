import json
from django.shortcuts import render
from Blog.models import User, Item, UserInventory, Skin, Rarity
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from Blog.views.inventory_views import get_items_list
import random as rd
from Blog.views.utils_views import get_item

@login_required
def atelier(request):


    non_legendary_item_id = Skin.objects.exclude(rarity__name = 'legendary').values_list('id', flat=True)

    user_inventory = UserInventory.objects.filter(user_id=request.user, item_id__type='skin', item__item_id__in=non_legendary_item_id)
    items = get_items_list(user_inventory)



    url = "Blog/atelier/atelier.html"
    context = {'items' : items}

    return render(request, url, context)


@login_required
def recycler(request):

    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return HttpResponseBadRequest('<h1>400 Bad Request</h1><p>Requête non autorisée.</p>')

    data = json.loads(request.body)

    item_ids = data.get('items_a_recycler')

    if len(item_ids) < 10:
        str_item = 'équipement' if len(item_ids) == 9 else 'équipements'
        return JsonResponse({"success" : False, "error" : f"Rajoutez encore {10 - len(item_ids)} {str_item} pour pouvoir recycler."})
    
    items = [Item.objects.get(id = item_id) for item_id in item_ids]
    skins = [Skin.objects.get(id = item.item_id) for item in items]
    rarities = [Rarity.objects.get(id = skin.rarity_id).name for skin in skins]

    # Check if same rarity
    if rarities.count(rarities[0]) != len(rarities):
        return JsonResponse({'success' : False, 'error' : "Vous ne pouvez recycler que des équipements de même rareté."})

    rarity = rarities[0]
    if rarity == 'legendary':
        return JsonResponse({'success' : False, 'error' : "Vous ne pouvez pas recycler d'équipements légendaires."})
    
    new_rarity = {'common' : 'uncommon',
                  'uncommon' : 'rare',
                  'rare' : 'legendary'}.get(rarity)
    
    new_skin = Skin.objects.filter(rarity_id = Rarity.objects.get(name=new_rarity))

    skin_id = rd.choice(new_skin).id

    item, skin = get_item(skin_id)

    item.save()

    UserInventory.objects.create(user = request.user,
                                 item = item)

    for item in items:
        item.delete()
    
    return JsonResponse({"success" : True, 
                         "skin_url" : skin.image.url,
                         "rarity_color" : skin.rarity.color,
                         "rarity_name" : skin.rarity.name,
                         "item_id" : item.id})

