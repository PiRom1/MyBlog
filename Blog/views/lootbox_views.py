from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..models import *
import random as rd
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
import json



def get_random_hexa_color():
    caracs = [str(i) for i in range(10)] + ['A', 'B', 'C', 'D', 'E', 'F']
    choices = rd.choices(caracs, k = 3)
    return '#' + ''.join(choices)

def get_random_animated_color():
    caracs = ['#F00','#F80','#FF0','#8F0','#090','#0F8','#0FF','#08F','#00F','#80F','#F0F','#F08','#000','rainbow']
    return rd.choice(caracs)


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

#     url = 'Blog/lootbox/openning.html'
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
    skins = [skin.image.url for skin in skins]
    
    context = {"skins" : skins}

    url = "Blog/lootbox/openning.html"
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
    skin = Skin.objects.get(id=item)
    if skin.type == 'font':
        item = Item(type='skin',
                    pattern=Font.objects.get(id=rd.randint(1,1112)).name,
                    item_id=item)
    elif skin.type == 'emoji' or skin.type == 'background_image':
        item = Item(type='skin',
                    pattern='',
                    item_id=item)
    # Il manque Border image
    elif skin.type == 'border_rgb' or skin.type == 'name_rgb':
        item = Item(type='skin',
                    pattern=get_random_animated_color(),
                    item_id=item)
    else:
        item = Item(type='skin',
                    pattern=get_random_hexa_color(),
                    item_id=item)
        
    itemUser = UserInventory(user=request.user,
                             item=item)   
    item.save()
    itemUser.save()

    request.user.coins -= open_price
    request.user.save()

    return JsonResponse({'status': 'success', 'message': 'Item dropped successfully!'})

@login_required
def get_lootbox(request):

    box = Item(type='box',
               item_id=1)
    
    box_user = UserInventory(user = request.user,
                             item = box)
    
    box.save()
    box_user.save()

    return HttpResponseRedirect('/inventory')
