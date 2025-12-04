import json
from django.shortcuts import render
from ..models import UserInventory, Item, Skin, Box, Market, MarketHistory, Emojis, Background, BorderImage
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import F
from Blog.views.quests_views import validate_objective_quest
from Blog.views.utils_views import write_journal_hdv_sold, write_journal_hdv_is_selling
import numpy as np


N_PER_PAGE = 10
MAX_PAGES = np.ceil(MarketHistory.objects.all().count() / N_PER_PAGE) - 1


def get_market_history(page = 0):
    """
    Return the history of the hdv for a certain page
    
    :param page: int, number of the page (the lower the more recent)
    """

    market_items = MarketHistory.objects.all().order_by('-date')

    if page > MAX_PAGES:
        raise("La page demandée n'existe pas")
 
    market_items = market_items[(N_PER_PAGE * page) : (N_PER_PAGE * (page + 1))]
    market_history = []

    for history in market_items:
        if history.item.type == 'skin':
            skin = Skin.objects.get(id=history.item.item_id).name
        else:
            skin = 'box'
        
        market_history.append({'user' : history.user.username,
                               'action' : history.action,
                               'price' : history.price,
                               'date' : history.date,
                               'skin' : skin,
                               'pattern' : history.item.pattern,
                               'price' : history.price if history.action == 'sell' else -history.price})

    return market_history



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
            url = Skin.objects.get(type='emoji').image.url

        if skin.type == 'background_image' and pattern != '':
            background = Background.objects.get(id=pattern)
            url = background.image.url
        
        if skin.type == 'background_image' and pattern == '':
            url = Skin.objects.get(type='background_image').image.url
        
        if skin.type == 'border_image' and pattern == '':
            url = Skin.objects.get(type='border_image').image.url
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
        

    context = {
        'selling_items' : selling_items,
        'your_items' : your_items,
        'user' : request.user,
        'max_pages' : MAX_PAGES
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
    

    write_journal_hdv_sold(seller = transaction.seller, buyer = request.user, item = item, price = transaction.price)

    # Delete market line
    transaction.delete()



    return JsonResponse({'success': True,
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

    # Valider la quête
    validate_objective_quest(user = request.user, action = "hdv")

    write_journal_hdv_is_selling(seller = request.user, item = item, price = price)


    return JsonResponse({'success': True,
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
    
    return JsonResponse({'success' : True,
                         'user' : request.user.username,
                         'item' : item_id})



@login_required
def remove_all(request):
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return HttpResponseBadRequest('<h1>400 Bad Request</h1><p>Requête non autorisée.</p>')
    
    # Get data
    user = request.user
    
    items = Market.objects.filter(seller=user)

    for item in items:
        UserInventory.objects.create(user = request.user,
                                     item = item.item)
        item.delete()
    
    return JsonResponse({'success' : True,
                         'user' : request.user.username})




@login_required
def get_market(request):
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return HttpResponseBadRequest('<h1>400 Bad Request</h1><p>Requête non autorisée.</p>')
    
    page = int(request.POST.get('page'))
    print(page, type(page))
    try:
        market = get_market_history(page = page)
        print(market[0])
        data = [{"item"}]
        return JsonResponse({"success" : True,
                             "market" : market})
    except Exception as e:
        print(f"Erreur : {e}")
        return JsonResponse({"success" : False})