 
from django.shortcuts import render, redirect
from ..models import *
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from ..forms import *
from django.contrib.auth.decorators import login_required
from ..utils.stats import *
import random as rd

from Blog.views.quests_views import validate_objective_quest



@login_required
def recit_list(request):
    recits = Recit.objects.all()
    nb_textes = []

    for recit in recits:
        texte = Texte.objects.filter(recit=recit)
        nb_textes.append(len(texte))
    

    context = {'recits' : zip(recits, nb_textes),
               }
    
    return render(request, 'Blog/recits/recit_list.html', context)

@login_required
def create_recit(request):
        
    if request.method == "POST":
        message_form = CharForm(request.POST)

        if message_form.is_valid():
            new_recit = Recit(name = message_form['message'].value())
            new_recit.save()

            return HttpResponseRedirect(f"/recits/detail/{new_recit.id}")
    
    message_form = CharForm()

    context = {'form' : message_form,
    }
    
    return render(request, 'Blog/recits/create_recit.html', context)


@login_required
def detail_recit(request, pk):
    
    recit = Recit.objects.get(pk=pk)
    texts = Texte.objects.filter(recit = recit)
    user = request.user

    if request.method == 'POST':
        form = MessageForm2(request.POST)

        if form.is_valid():

            texte = form['message'].value()
            texte = Texte(text = texte, user = user, recit = recit)
            texte.save()

            validate_objective_quest(user = request.user, action = "recit")
            

            return HttpResponseRedirect('.#bottom')
    
    form = MessageForm2()

    if not texts:
        is_last_writer = False
    else:
        is_last_writer = list(texts)[-1].user == user
    
    
    print(is_last_writer)
    context = {'form' : form, 
               'recit' : recit,
               'texts' : texts,
               'is_last_writer' : is_last_writer}
    
    return render(request, 'Blog/recits/detail_recit.html', context)


