from Blog.models import Item, User, UserInventory, Skin
from Blog.views.utils_views import get_item

def run():

    user = User.objects.get(username='romain')

    skins = Skin.objects.all()
    
    for _ in range(10):
        for skin in skins:
            item, skin = get_item(skin.id)
            item.save()
            UserInventory.objects.create(user = user, item = item)

