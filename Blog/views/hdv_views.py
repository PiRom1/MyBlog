import json
from django.shortcuts import render
from ..models import UserInventory, Item, Skin, Box, Market, MarketHistory, Emojis, Background, BorderImage
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import F




def list_hdv(request):
    
    selling_items = []
    your_items = []

    for item in Market.objects.all():
        print("item : ", item.item)
        market_id = item.id
        item_id = item.item_id
        seller = item.seller
        item_ = item.item
        skin = Skin.objects.get(pk = item_.item_id)
        price = item.price
        pattern = item_.pattern
        url = ''

        if skin.type == 'emoji' and pattern != '':
            emoji = Emojis.objects.get(id=pattern)
            url = emoji.image.url
        
        if skin.type == 'emoji' and pattern == '':
            url = Skin.objects.get(name='emoji').image.url

        if skin.type == 'background_image' and pattern != '':
            background = Background.objects.get(id=pattern)
            url = background.image.url
        
        if skin.type == 'background_image' and pattern == '':
            url = Skin.objects.get(name='background_image').image.url
        
        if skin.type == 'border_image' and pattern == '':
            url = Skin.objects.get(name='border_image').image.url
        if skin.type == 'border_image' and pattern != '':
            url = BorderImage.objects.get(name=pattern).image.url

        type = skin.type if item.item.type == 'skin' else 'Box'

        d = {'market_id' : market_id,
             'item_id' : item_id,
             'seller' : seller,
             'item' : item,
             'type' : type,
             'price' : price,
             'pattern' : pattern,
             'url' : url}
        
        print(d)
        
        your_items.append(d) if seller == request.user else selling_items.append(d)
    
    market_history = []

    for history in MarketHistory.objects.all().order_by('-date'):
        if history.item.type == 'skin':
            skin = Skin.objects.get(id=history.item.item_id).name
        else:
            skin = 'box'
        
        market_history.append({'history' : history,
                               'skin' : skin,
                               'pattern' : history.item.pattern,
                               'price' : history.price if history.action == 'sell' else -history.price})



    context = {
        'selling_items' : selling_items,
        'your_items' : your_items,
        'user' : request.user.username,
        'market_history' : market_history,
    }
    
    return render(request, 'Blog/hdv/hdv.html', context)



@login_required
def buy(request):
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return HttpResponseBadRequest('<h1>400 Bad Request</h1><p>Requête non autorisée.</p>')
    
    user = request.user
    id = request.POST.get('id')
    
    # Get transaction and item
    transaction = Market.objects.get(pk=id)

    # Check if enough coins
    if request.user.coins < transaction.price:
        return HttpResponseRedirect('/hdv')

    item = Item.objects.get(pk=transaction.item.id)
    
    
    # Add item to buyer's inventory
    buyer_item = UserInventory(user = request.user, item = item)
    buyer_item.save()

    # diplodocoin transaction
    user.coins = F('coins') - transaction.price
    user.save(update_fields=['coins'])  # Enregistre uniquement le champ `count`
    user.refresh_from_db()

    transaction.seller.coins = F('coins') + transaction.price
    transaction.seller.save(update_fields=['coins'])
    transaction.seller.refresh_from_db()


    # Make market history
    history_buyer = MarketHistory(user = request.user,
                                  item = item,
                                  price = -transaction.price,
                                  action = "buy")
    history_buyer.save()
    

    # Delete market line
    transaction.delete()


    return JsonResponse({'success': 'success',
                         'item_id' : item.item_id,
                         'price' : transaction.price,
                         'buyer' : request.user.username,
                         'seller' : transaction.seller.username,
                         })




@login_required
def sell(request):
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return HttpResponseBadRequest('<h1>400 Bad Request</h1><p>Requête non autorisée.</p>')
    
    # Get data
    user = request.user
    item_id = request.POST.get('item_id')
    id = request.POST.get('id')
    price = request.POST.get('price')
    
    if id:
        item_id = id
    
    item = Item.objects.get(pk=item_id)

    # Mettre en vente
    vente = Market(seller = user, 
                   item = item, 
                   price = price)
    
    vente.save()

    # sortir de l'inventaire
    UserInventory.objects.get(item_id=item_id).delete()

    # Market history
    MarketHistory.objects.create(price = price,
                                 action = 'sell',
                                 item = item,
                                 user = user)

    # Taxe à voir + tard


    return JsonResponse({'success': 'success',
                         'item_id' : item.item_id,
                         'price' : price,
                         'seller' : user.username,
                         })



@login_required
def remove(request):
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return HttpResponseBadRequest('<h1>400 Bad Request</h1><p>Requête non autorisée.</p>')
    
    # Get data
    user = request.user
    item_id = request.POST.get('id')
    print(item_id)
    vente = Market.objects.get(item_id=item_id)
    vente.delete()

    UserInventory(user = request.user,
                  item = Item.objects.get(pk=item_id)).save()
    
    return JsonResponse({'success' : 'success',
                         'user' : request.user.username,
                         'item' : item_id})