import json
from django.shortcuts import render
from ..models import UserInventory, Item, Skin, Box, Market, MarketHistory
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import F




def list_hdv(request):
    
    selling_items = []
    your_items = []

    for item in Market.objects.all():
        market_id = item.id
        item_id = item.item_id
        seller = item.seller
        item_ = item.item
        skin = Skin.objects.get(pk = item_.item_id)
        price = item.price
        pattern = item_.pattern

        d = {'market_id' : market_id,
             'item_id' : item_id,
             'seller' : seller,
             'item' : item,
             'type' : skin.type,
             'price' : price,
             'pattern' : pattern}
        
        your_items.append(d) if seller == request.user else selling_items.append(d)
    


    

    context = {
        'selling_items' : selling_items,
        'your_items' : your_items,
        'user' : request.user.username,
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
    item = Item.objects.get(pk=transaction.item.id)
    
    # Delete item from seller's inventory
    seller_item = UserInventory.objects.filter(user=transaction.seller)
    seller_item.delete()

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
    
    history_seller = MarketHistory(user = transaction.seller,
                                  item = item,
                                  price = transaction.price,
                                  action = "sell")
    history_seller.save()

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
    price = request.POST.get('price')
    
    item = Item.objects.get(pk=item_id)

    # Mettre en vente
    vente = Market(seller = user, 
                   item = item, 
                   price = price)
    
    vente.save()

    # sortir de l'inventaire
    UserInventory.objects.get(item_id=item_id).delete()

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
    
    vente = Market.objects.get(item_id=item_id)
    vente.delete()

    UserInventory(user = request.user,
                  item = Item.objects.get(pk=item_id)).save()
    
    return JsonResponse({'success' : 'success',
                         'user' : request.user.username,
                         'item' : item_id})