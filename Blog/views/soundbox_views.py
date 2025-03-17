from django.shortcuts import render, redirect
from ..models import *
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from ..forms import *
from django.contrib.auth.decorators import login_required
from django.conf import settings

from Blog.views.quests_views import validate_objective_quest


from ..utils.stats import *
import random as rd





@login_required
def list_sounds(request):

    all_sounds = Sound.objects.all()
    user = request.user
    print(all_sounds)
    checks = []
    tags = []
    for sound in all_sounds:
        
        is_checked = UserSound.objects.filter(sound=sound).filter(user=user)
        checks.append(len(is_checked) >= 1)
        tags.append(sound.tags)

    print(checks)

    
    url = "Blog/soundbox/list_sounds.html"

    context = {'all_sounds' : zip(all_sounds, checks, tags),
               "media_path" : settings.MEDIA_URL,
               "nb_sounds" : len(all_sounds),
               }

    return render(request, url, context)


def add_sounds(request):

    
    if request.method == "POST":
        sound_form = SoundForm(request.POST, request.FILES)
        print(sound_form)

        if sound_form.is_valid():
            instance = sound_form.save(commit=False)
            instance.user = request.user
            instance.save()

            sound_id = instance.id
            sound = Sound.objects.get(id=sound_id)
            for user in User.objects.all():
                UserSound(user=user, sound = sound).save()

            validate_objective_quest(user = request.user, action = "soundbox")

            return HttpResponseRedirect('/list_sounds')
        else:
            print(sound_form.errors)
    
    sound_form = SoundForm()


    url = "Blog/soundbox/add_sounds.html"

    context = {'sound_form' : sound_form,
               }

    return render(request, url, context)




def update_soundbox(request):
    
    user = request.user
    print("available sounds : ")
    print(UserSound.objects.filter(user=user))
    print(1)
    sound = request.GET.get('sound',1)
    sound = Sound.objects.get(id=sound)
    print(sound)
    

    soundForUser = UserSound.objects.filter(user=user).filter(sound=sound)

    if soundForUser:
        soundForUser.delete()
    else:
        new_soundForUser = UserSound(sound = sound, user = user).save()

    print(soundForUser)


    json = {'attribute' : 1,
            'checked' : True}
    
    return JsonResponse(json, status=200)


def increment_sound(request):
    print(1)
    sound = request.GET.get('sound',1)

    if '/' in sound: # Si lien
        sound = sound.split('/')[-1]
        sound = "Soundbox/" + sound
        print("name : ", sound)
        sound = Sound.objects.filter(sound=sound)[0]

    else: # Si int (id)
        sound = Sound.objects.get(id=sound)

    sound.counter += 1
    sound.save()
    print(sound.counter)

    return JsonResponse({'sound' : sound.name,
                        'counter' : sound.counter}, status=200)



