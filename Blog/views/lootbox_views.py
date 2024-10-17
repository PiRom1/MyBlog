from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..models import *
import random as rd


def get_random_hexa_color():

    caracs = [str(i) for i in range(10)] + ['a', 'b', 'c', 'd', 'e', 'f']
    choices = rd.choices(caracs, k = 6)

    return '#' + ''.join(choices)


@login_required
def open_lootbox(request, pk):

    box = Box.objects.get(pk=pk)
    skins = list(Skin.objects.filter(box_id=box.id))
    print("Skins : ", skins)
    # Choix de l'item : (pour l'instant proba uniforme, mais à terme need probas définies)
    item = rd.choice(skins)
    print("Item : ", item)
    random_color = get_random_hexa_color()
    item = Item(type="skin", pattern = random_color)
    user_item = UserInventory(user = request.user, 
                              item = item,
                              status = 'unequipped',
                              )
    item.save()
    user_item.save()

    url = 'Blog/lootbox/openning.html'
    return render(request, url)

@login_required
def view_lootbox(request, pk):
    box = Box.objects.get(pk=pk)
    skins = list(Skin.objects.filter(box_id=box.id))
    print("Skins : ", skins)

    context = {'skins' : skins}
    url = 'Blog/lootbox/view_box.html'
    return render(request, url, context)