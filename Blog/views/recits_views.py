 
from django.shortcuts import render, redirect
from ..models import *
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from ..forms import *
from django.contrib.auth.decorators import login_required
from ..utils.stats import *
import random as rd
from Blog.views.utils_views import write_journal_recit_create, write_journal_recit_contribute, username_to_rgb, complementary_color

from Blog.views.quests_views import validate_objective_quest



@login_required
def recit_list(request):
    recits = Recit.objects.all()
    nb_textes = []
    nb_writers = []
    are_you_last_writer = []
    first_text = []

    for recit in recits:
        textes = Texte.objects.filter(recit=recit)
        nb_textes.append(len(textes))
        nb_writers.append(len(set([texte.user.id for texte in textes])))
        are_you_last_writer.append(list(textes)[-1].user == request.user)
        first_text.append(textes[0].text)
    

    context = {'recits' : zip(recits, nb_textes, nb_writers, are_you_last_writer, first_text)}
    
    return render(request, 'Blog/recits/recit_list.html', context)

@login_required
def create_recit(request):
        
    if request.method == "POST":
        message_form = CharForm(request.POST)

        if message_form.is_valid():
            new_recit = Recit(name = message_form['message'].value())
            new_recit.save()

            write_journal_recit_create(user = request.user, recit = new_recit)

            return HttpResponseRedirect(f"/recits/detail/{new_recit.id}")
    
    message_form = CharForm()

    context = {'form' : message_form,
    }
    
    return render(request, 'Blog/recits/create_recit.html', context)


@login_required
def detail_recit(request, pk):
    
    recit = Recit.objects.get(pk=pk)
    texts = Texte.objects.filter(recit = recit)
    message_colors = [
        f"rgb({r}, {g}, {b})"
        for r, g, b in (username_to_rgb(text.user.username) for text in texts)
    ]

    text_colors = [    
        f"rgb({r}, {g}, {b})"
        for r, g, b in (
            complementary_color(username_to_rgb(text.user.username))
            for text in texts
        )
    ]

    user = request.user

    if request.method == 'POST':
        form = MessageForm2(request.POST)

        if form.is_valid():

            texte = form['message'].value()
            texte = Texte(text = texte, user = user, recit = recit)
            texte.save()

            validate_objective_quest(user = request.user, action = "recit")

            write_journal_recit_contribute(user = request.user, recit = recit)
            

            return HttpResponseRedirect('.#bottom')
    
    form = MessageForm2()

    if not texts:
        is_last_writer = False
    else:
        is_last_writer = list(texts)[-1].user == user
    
    
    print(is_last_writer)
    context = {'form' : form, 
               'recit' : recit,
               'texts' : zip(texts, message_colors, text_colors),
               'is_last_writer' : is_last_writer}
    
    return render(request, 'Blog/recits/detail_recit.html', context)


