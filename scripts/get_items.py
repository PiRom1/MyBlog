from Blog.models import Item, User, UserInventory, Skin


def run():

    user = User.objects.get(username='romain')

    skins = Skin.objects.all()

    for skin in skins:

        if skin.name == 'emoji' or skin.name == 'background_image':
            pattern = ''
        else:
            pattern = '#abc'

        item = Item.objects.create(type='skin',
                                   pattern = pattern,
                                   item_id = skin.id)
        
        UserInventory.objects.create(user=  user, 
                                     item = item)
