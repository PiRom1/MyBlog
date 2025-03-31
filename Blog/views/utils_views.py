from django.shortcuts import render, redirect

from ..models import *
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from ..forms import *
from django.contrib.auth.decorators import login_required

from ..utils.stats import *
import random as rd
import json



@login_required
def getSession(request):
    
    user = request.user
    connecte = user.is_authenticated

    if not connecte:
        return HttpResponseRedirect("/login/")

    print(connecte)

    su = SessionUser.objects.filter(user = user)
    sessions = Session.objects.filter(id__in = [session.session_id for session in su])
    print(sessions)
    context = {"sessions" : sessions, "user" : user}
    return render(request, "Blog/get_session.html", context)



@login_required
def get_moderaptor(request):
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return HttpResponseBadRequest('<h1>400 Bad Request</h1><p>Requête non autorisée.</p>')
    
    response = {'success' : True, 'log' : 'You got Moderaptor. Enjoy !'}

    print('repsonse : ', response)
    return JsonResponse(response)




def get_random_hexa_color():
    caracs = [str(i) for i in range(10)] + ['A', 'B', 'C', 'D', 'E', 'F']
    choices = rd.choices(caracs, k = 3)
    return '#' + ''.join(choices)

def get_random_animated_color():
    caracs = ['#F00','#F80','#FF0','#8F0','#090','#0F8','#0FF','#08F','#00F','#80F','#F0F','#F08','#000','rainbow']
    return rd.choice(caracs)


def get_item(skin_id):

    # Instantiate new item
    skin = Skin.objects.get(id=skin_id)

    if skin.type == 'font':
        item = Item(type='skin',
                    pattern=Font.objects.get(id=rd.randint(1,1112)).name,
                    item_id=skin_id)
    elif skin.type == 'emoji' or skin.type == 'background_image':
        item = Item(type='skin',
                    pattern='',
                    item_id=skin_id)
    # Il manque Border image
    elif skin.type == 'border_rgb' or skin.type == 'name_rgb':
        item = Item(type='skin',
                    pattern=get_random_animated_color(),
                    item_id=skin_id)
    elif skin.type == 'border_image':
        border_images = BorderImage.objects.all().values_list('name', flat=True)
        item = Item(type='skin',
                    pattern = rd.choice(border_images),
                    item_id=skin_id)
    else:
        item = Item(type='skin',
                    pattern=get_random_hexa_color(),
                    item_id=skin_id)
    

    return item, skin