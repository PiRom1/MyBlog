from Blog.models import User, UserInventory, Item, Skin, Market, MarketHistory


def run():

    for market in Market.objects.all():
        print(market.item)

        if not UserInventory.objects.filter(item = market.item).exists():
            print(f"Remise dans l'inventaire de l'objet {market.item}")
            UserInventory.objects.create(user = market.seller,
                                         item = market.item)
        
        print("Suppression dans l'hdv de l'item {market.item}")
        Market.objects.filter(id = market.id).delete()