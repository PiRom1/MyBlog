from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..models import *
import random as rd
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
import json
from Blog.views.utils_views import get_item




# @login_required
# def open_lootbox(request, pk):

#     box = Box.objects.get(pk=pk)
#     skins = list(Skin.objects.filter(box_id=box.id))
#     print("Skins : ", skins)
#     # Choix de l'item : (pour l'instant proba uniforme, mais à terme need probas définies)
#     item = rd.choice(skins)
#     print("Item : ", item)
#     random_color = get_random_hexa_color()

#     # Pas d'attribution tant que tout n'est pas dev

#     # item = Item(type="skin", pattern = random_color)
#     # user_item = UserInventory(user = request.user, 
#     #                           item = item,
#     #                           status = 'unequipped',
#     #                           )
#     # item.save()
#     # user_item.save()

#     url = 'Blog/lootbox/opening.html'
#     return render(request, url)

@login_required
def view_lootbox(request, pk):
    box = Box.objects.get(pk=pk)
    box_img = box.image.url
    open_price = box.open_price
    skins = list(Skin.objects.filter(box_id=box.id))
    print("Skins : ", skins)
    skins = zip([skin.type for skin in skins], [skin.image.url for skin in skins])

    can_open = request.user.coins >= open_price

    context = {'skins' : skins,
               'box_id': pk,
               'box_img' : box_img,
               'open_price' : open_price,
               'can_open' : can_open}
    
    url = 'Blog/lootbox/view_box.html'
    return render(request, url, context)


@login_required
def open_lootbox(request):
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return HttpResponseBadRequest('<h1>400 Bad Request</h1><p>Requête non autorisée.</p>')
    
    skins = list(Skin.objects.all())
    skin_images = [skin.image.url for skin in skins]
    skin_probas = [skin.rarity.probability for skin in skins]
    # dictionnaire comptant le nombre de skins de chaque proba
    proba_dict = {proba:0 for proba in skin_probas}
    for proba in skin_probas:
        proba_dict[proba] += 1
    
    skin_probas = [proba/proba_dict[proba] for proba in skin_probas]

    rarity_colors = [skin.rarity.color for skin in skins]
    
    context = {"skin_images" : skin_images,
               "skin_probas" : skin_probas,
               "rarity_colors" : rarity_colors}

    url = "Blog/lootbox/opening.html"
    return render(request, url, context)


@login_required
def drop_item(request):
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return HttpResponseBadRequest('<h1>400 Bad Request</h1><p>Requête non autorisée.</p>')
    # Get data
    data = json.loads(request.body)
    item = data.get('item') 
    # Delete box in user inventory
    box = UserInventory.objects.filter(item_id__type='box').filter(user_id=request.user).first()
    box_id = box.item_id
    open_price = Box.objects.get(pk = box.item.item_id).open_price
    box.delete()
    
    # Delete box in items
    Item.objects.get(id=box_id).delete()
    # Instantiate new item
    item, skin = get_item(item)
        
    itemUser = UserInventory(user=request.user,
                             item=item)   
    item.save()
    itemUser.save()

    request.user.coins -= open_price
    request.user.save()

    OpeningLog(user=request.user,
                skin=skin).save()

    return JsonResponse({'status': 'success', 'message': 'Item dropped successfully!'})

@login_required
def get_lootbox(request):
    for _ in range(10):
        UserInventory.objects.create(user=request.user, item=Item.objects.create(type='box', item_id=1))

    return HttpResponseRedirect('/inventory')
