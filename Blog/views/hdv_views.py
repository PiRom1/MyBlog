import json
from django.shortcuts import render
from ..models import UserInventory, Item, Skin, Box, Market, MarketHistory
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import F




def list_hdv(request):
    
    selling_items = Market.objects.all()
    ids = [item.id for item in selling_items]
    sellers = [item.seller for item in selling_items]
    items = [item.item for item in selling_items]
    skins = [Skin.objects.get(pk=item.item_id).type for item in items]
    prices = [item.price for item in selling_items]
    patterns = [item.pattern for item in items]


    items = {'patterns' : patterns,
             'skins' : skins}
    
    print("items : ", items, skins)
    

    context = {
        'sellers' : sellers,
        'items' : items,
        'prices' : prices,
        'ids' : ids,
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
