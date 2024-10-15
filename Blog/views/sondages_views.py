from django.shortcuts import render, redirect
from ..models import *
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from ..forms import *
from django.contrib.auth.decorators import login_required

from ..utils.stats import *
import random as rd




@login_required
def sondage_list(request):
    sondages = Sondage.objects.all()
    current_sondages = sondages.filter(current=True)
    older_sondages = sondages.filter(current=False)

    context = {'sondages' : sondages,
               'current_sondages' : current_sondages,
               'older_sondages' : older_sondages}
    
    return render(request, 'Blog/sondages/sondage_list.html', context)



@login_required
def update_sondage(request, pk):
    sondage = Sondage.objects.get(pk=pk)
    choices = SondageChoice.objects.filter(sondage=sondage)

    
    if request.method == 'POST':
        form = SondageForm(request.POST, instance=sondage)
        formset = ChoiceFormSet0(request.POST, queryset=choices)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()

            # Si nouveau current et qu'il y en avait un autre : devient le seul nouveau current. 
            for _sondage in Sondage.objects.all():
                if _sondage.current and _sondage != sondage:
                    _sondage.current = False
                    _sondage.save()


            return redirect('sondage_list')
        
            
    else:
        
        form = SondageForm(instance=sondage)
        formset = ChoiceFormSet0(queryset=choices)
    return render(request, 'Blog/sondages/update_sondage.html', {'form': form, 'sondage': sondage, 'formset' : formset})



@login_required
def create_sondage(request):
    
    if request.method == 'POST':
        form = SondageForm(request.POST)
        formset = ChoiceFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            form.save()
            
            for choice_form in formset:
                choice_data = choice_form.cleaned_data
                print(choice_data)
                if choice_data:
                    choice = choice_data['choice']
                    new_choice = SondageChoice(choice = choice, sondage = Sondage.objects.filter(id=form.instance.id)[0])
                    new_choice.save()

            # Si nouveau current et qu'il y en avait un autre : devient le seul nouveau current. 
            sondage = Sondage.objects.filter(id=form.instance.id)[0]
            for _sondage in Sondage.objects.all():
                if _sondage.current and _sondage != sondage:
                    _sondage.current = False
                    _sondage.save()


            return redirect('sondage_list')
    else:
        form = SondageForm()
        formset = ChoiceFormSet()
        last_message = Message.objects.last()
        code = (last_message.text.split(':')[0]).lower().strip()
        if code == "sondage":
            form.fields['question'].initial = last_message.text.split(':',1)[1]
            last_message.delete()

    return render(request, 'Blog/sondages/create_sondage.html', {'form': form, 'choice_forms' : formset})


@login_required
def delete_sondage(request, pk):
    Sondage.objects.filter(pk=pk)[0].delete()

    return HttpResponseRedirect('/sondages')


@login_required
def detail_sondage(request, pk):
    sondage = Sondage.objects.filter(pk = pk)[0]
    choices = SondageChoice.objects.filter(sondage = sondage)

    context = {'sondage' : sondage,
               'choices' : choices}
    
    url = 'Blog/sondages/detail_sondage.html'

    return render(request, url, context)


@login_required
def vote_sondage(request, sondage_id, choice_id):
    
    sondage = Sondage.objects.filter(id=sondage_id)[0]
    choice = SondageChoice.objects.filter(id=choice_id)[0]
    user = request.user
    can_vote = True
    for choice_user in ChoiceUser.objects.filter(user=user):
        if choice_user.choice.sondage.id == sondage_id:
            choice_user.delete()
            if choice_user.choice_id == choice_id:
                can_vote = False
    
    print("User : ", user.id)
    if can_vote:
        choice_user = ChoiceUser(choice = choice, user = user)
        choice_user.save()


    return HttpResponseRedirect(f"{request.session.get('previous_url', '/')}#bottom")
