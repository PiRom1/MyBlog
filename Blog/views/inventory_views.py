import json
from django.shortcuts import render
from ..models import UserInventory, Item, Skin, Box, Emojis, Background, BorderImage
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from ..forms import EmojiForm, BackgroundForm
import random as rd

def get_skin_type(type):
    if type == 'text_color':
        return 'Couleur de texte'
    if type == 'background_color':
        return 'Couleur de fond'
    if type == 'avatar_color':
        return 'Couleur d\'avatar'
    if type == 'name_color' or type == 'name_rgb':
        return 'Couleur de nom'
    if type == 'border_color' or type == 'border_image' or type == 'border_rgb':
        return 'Bordure de message'
    if type == 'font':
        return 'Police'
    return 'Autre'



def get_items_list(user_inventory):
    items = []

    for inventory in user_inventory:
        item = inventory.item
        
        # Si l'item est un box
        if item.type == 'box':
            box = Box.objects.get(id=item.item_id)
            items.append({
                'type': 'box',
                'id' : item.id,
                'item_id': item.item_id,
                'name': box.name,
                'image': box.image.url,
                'open_price': box.open_price,
                'equipped': inventory.equipped,
                'favorite': inventory.favorite,
                'obtained_date': inventory.obtained_date
            })
        # Si l'item est un skin
        elif item.type == 'skin':
            skin = Skin.objects.get(id=item.item_id)
            print(item)
            print(item.id)
            items.append({
                'type': 'skin',
                'item_id': item.id,
                'name': skin.name,
                'image': skin.image.url,
                'pattern': item.pattern,
                'equipped': inventory.equipped,
                'favorite': inventory.favorite,
                'obtained_date': inventory.obtained_date,
                'skin_type': skin.type,
                'rarity_name': skin.rarity.name,
                'rarity_color': skin.rarity.color
                })
            
            if skin.type == 'emoji' and item.pattern != '':
                emoji = Emojis.objects.get(id=item.pattern)
                print(items[-1]['image'])
                items[-1]['image'] = emoji.image.url
            
            if skin.type == 'background_image' and item.pattern != '':
                background = Background.objects.get(id=item.pattern)
                items[-1]['image'] = background.image.url
            
            if skin.type == 'border_image':
                print("pattern : ", item.pattern)
                border_image = BorderImage.objects.get(name=item.pattern)
                items[-1]['url'] = border_image.image.url
    
    return items


@login_required
def user_inventory_view(request):
    # Récupérer l'inventaire de l'utilisateur connecté
    # Trier par date d'obtention inverse
    user_inventory = UserInventory.objects.filter(user=request.user).order_by('-obtained_date')
    
    # Récupérer les informations pour chaque item d'inventaire
    items = get_items_list(user_inventory)
    

    background_id = Skin.objects.get(type='background_image').id
    bg = UserInventory.objects.filter(item_id__item_id=background_id).filter(equipped=True)
    if bg:
        bg = Background.objects.get(id = bg[0].item.pattern).image.url
    else:
        bg = None


    context = {
        'items': items,
        'coins' : request.user.coins,
        'bg' : bg,

    }
    
    return render(request, 'Blog/inventory/inventory.html', context)

@login_required
def toggle_item_favorite(request):
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return HttpResponseBadRequest('<h1>400 Bad Request</h1><p>Requête non autorisée.</p>')
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        new_favorite = request.POST.get('favorite')

        print("id ; ", item_id)

        # Trouver l'item dans l'inventaire de l'utilisateur connecté
        try:
            inventory_item = UserInventory.objects.get(item_id=item_id, user=request.user)
            inventory_item.favorite = (new_favorite == 'True')
            print("new_favorite : ", new_favorite)
            inventory_item.save()
            return JsonResponse({'success': True, 'message': 'Statut mis à jour avec succès.'})
        except UserInventory.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Item non trouvé.'})

    return JsonResponse({'success': False, 'message': 'Requête invalide.'})


@login_required
def get_favorite_skins(request):
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return HttpResponseBadRequest('<h1>400 Bad Request</h1><p>Requête non autorisée.</p>')
    user = request.user
    items = UserInventory.objects.filter(user=user).filter(favorite=True)
    favorite_items = []
    for item in items:
        skin = Skin.objects.get(id=item.item.item_id)
        favorite_items.append({
            'name': skin.name,
            'skinType': get_skin_type(skin.type),
            'pattern': item.item.pattern,
            'id': item.item.id,
            'equipped': item.equipped
        })
    return JsonResponse({'favorite_items': favorite_items})

@login_required
def update_equipped(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
        item_id = data.get('item_id')
        old_equipped = data.get('previous_item_id')
        print("item_id : ", item_id, type(item_id))
        print("old_equipped : ", old_equipped, type(old_equipped))
        
        try:
            # Manage same item (unequip)
            if item_id:
                item = UserInventory.objects.get(user=request.user, item_id=item_id)
                if item.equipped:
                    item.equipped = False
                    item.save()

                    # get new_skins
                    items = UserInventory.objects.filter(user=request.user).filter(equipped=True)
                    item_ids = [item.item.item_id for item in items]
                    dict_items = {}

                    for i,item_id in enumerate(item_ids):
                        skin = Skin.objects.get(id=item_id).type
                        dict_items[skin] = items[i].item.pattern
                    if 'name_rgb' in dict_items and 'avatar_color' in dict_items:
                        del dict_items['avatar_color']
                    if 'border_image' in dict_items:
                        dict_items['border_image'] = BorderImage.objects.get(name=dict_items['border_image']).image.url

                    return JsonResponse({'status': 'success', 'action' : 'unequip', 'skins' : str(dict_items)})
            try :
                old_item = UserInventory.objects.get(user=request.user, item_id=old_equipped)
            except :
                pass
            else :
                old_item.equipped = False
                old_item.save()
            item = UserInventory.objects.get(user=request.user, item_id=item_id)
            item.equipped = True
            item.save()

            # get new_skins
            items = UserInventory.objects.filter(user=request.user).filter(equipped=True)
            item_ids = [item.item.item_id for item in items]
            dict_items = {}

            for i,item_id in enumerate(item_ids):
                skin = Skin.objects.get(id=item_id).type
                dict_items[skin] = items[i].item.pattern
            if 'name_rgb' in dict_items and 'avatar_color' in dict_items:
                del dict_items['avatar_color']
            if 'border_image' in dict_items:
                dict_items['border_image'] = BorderImage.objects.get(name=dict_items['border_image']).image.url


            return JsonResponse({'status': 'success', 'action' : 'equip', 'skins' : str(dict_items)})
        except UserInventory.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Item not found'}, status=404)
    return HttpResponseBadRequest('<h1>400 Bad Request</h1><p>Requête non autorisée.</p>')


@login_required
def use_emoji(request, pk):

    emoji = Item.objects.get(id=pk)
    

    if request.method == 'POST':
    
        emoji_form = EmojiForm(request.POST, request.FILES)

        if emoji_form.is_valid():
            
            instance = emoji_form.save()
            print(instance.id)
            print(instance.name, instance.image)

            emoji.pattern = instance.id
            emoji.save()

            return HttpResponseRedirect('/inventory')
    
    emoji_form = EmojiForm()

    url = "Blog/inventory/emoji.html"

    context = {'emoji_form' : emoji_form}

    return render(request, url, context)





@login_required
def use_bg(request, pk):

    bg = Item.objects.get(id=pk)



    if request.method == 'POST':
    
        bg_form = BackgroundForm(request.POST, request.FILES)

        if bg_form.is_valid():
            
            instance = bg_form.save()
            print(instance.id)
            print(instance.name, instance.image)

            if request.user.username == 'arnaud':
                background = Background.objects.get(id=instance.id)
                background.image.name = f'Bois/bois{rd.randint(1, 5)}.jpg'
                background.save()

            bg.pattern = instance.id
            bg.save()

            return HttpResponseRedirect('/inventory')
    
    bg_form = BackgroundForm()

    url = "Blog/inventory/bg.html"

    context = {'bg_form' : bg_form}

    return render(request, url, context)


@login_required
def equip_bg(request):

    # Get data
    item_id = request.POST.get('item_id')
    bg = Item.objects.get(pk=item_id)

    # Unequipp bg
    user_bgs = UserInventory.objects.filter(item_id__item_id = bg.item_id)
    for user_bg in user_bgs:
        user_bg.equipped = False
        user_bg.save()



    # Equip bg
    bg_id = bg.pattern
    bg = Background.objects.get(pk=bg_id)
    user_item = UserInventory.objects.get(item_id=item_id)
    user_item.equipped = True
    user_item.save()

    return JsonResponse({'bg_url' : bg.image.url})



@login_required
def unequip_bg(request):

    # Get data
    item_id = request.POST.get('item_id')
    bg = Item.objects.get(pk=item_id)

    # Unequipp bg
    user_bgs = UserInventory.objects.filter(item_id__item_id = bg.item_id)

    for user_bg in user_bgs:
        user_bg.equipped = False
        user_bg.save()

    return JsonResponse({'success' : True})