# context_processors.py

from .models import Skin, UserInventory, Background

def background_context(request):
    background_id = Skin.objects.get(type='background_image').id
    bg = UserInventory.objects.filter(item_id__item_id=background_id).filter(equipped=True)
    if bg:
        bg = Background.objects.get(id=bg[0].item.pattern).image.url
    else:
        bg = None
    return {'bg_url': bg}
