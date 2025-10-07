

from django.contrib.auth.decorators import login_required
from django.utils import timezone
from Blog.models import EnjoyTimestamp, User
from Blog.forms import EnjoyTimestampForm
from django.db.models.functions import ExtractHour, ExtractMinute
from django.db.models import Count, Avg, Q
import json
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
import numpy as np
from datetime import datetime, time
from django.utils.timezone import now

from Blog.views.quests_views import validate_objective_quest


def get_scale(values, scale = 400):
    """
    returns a list of scales according to the values list provided
    """

    # Get min and max values
    if values:
        max_value = max(max(values), 1)
        min_value = max(min(values), 1)
    else:
        max_value = 1
        min_value = 1

    # Compute values range
    ecart = int(np.ceil(max_value - min_value + 2))
    scale_values = [(i+1)*scale/ecart for i in range(ecart-1)]

    return scale_values






@login_required
def enjoy_timeline(request):

    url = "Blog/enjoy_timeline/enjoy_timeline.html"

    MIN_HOUR = 8
    MAX_HOUR = 20

    hours =  [i for i in range(MIN_HOUR, MAX_HOUR)]
    minutes = [i for i in range(0, 60)]

    timestamps_data = {}



    timestamps = EnjoyTimestamp.objects.annotate(
    hour=ExtractHour('time'), 
    minute=ExtractMinute('time')).values('hour', 'minute').annotate(count=Count('id'),
                                                                    mean_note=Avg('note', filter=Q(note__isnull=False))).order_by('hour', 'minute')

    default_stamp_color = [200, 200, 200]
    default_note_color = [200, 200, 200]

    timestamps = list(timestamps)
    stamp_values = [i['count'] for i in timestamps]
    note_values = [i['mean_note'] for i in timestamps if i["mean_note"]]

    scale = 400
    
    stamps_scale = get_scale(stamp_values, scale)
    notes_scale = get_scale(note_values, scale)
    
    for timestamp in timestamps:

        nb_timestamps = timestamp.get("count")
        nb_timestamps = nb_timestamps if nb_timestamps else 0
        if nb_timestamps == 0:
            new_stamp_color = default_stamp_color
        else:
            color = stamps_scale[nb_timestamps-1]
            if color <= 220:
                new_stamp_color = [255, 220-color, 220-color]
            else:
                color = color - 220
                new_stamp_color = [255-color, 0, 0]
        

        mean_note = timestamp.get("mean_note")
        mean_note = mean_note if mean_note else 0
        if not mean_note:
            note_color = default_note_color
        else:
        
            max_color = 255
            min_color = 0
            # Convertir une note entre 1 et 5 sur une valeur entre min et max. 
            ratio = mean_note / 4
            factor = ratio   # plus tu augmentes l’exposant, plus ça accentue les différences en haut
            note_color = [255,
                        max_color - (max_color - min_color) * factor,
                        max_color - (max_color - min_color) * factor,
                        ]

        

        
        timestamps_data[f"{timestamp['hour']}_{timestamp['minute']}"] = {"stamps_count" : timestamp['count'],
                                                                         "mean_note" : timestamp["mean_note"],
                                                                         "stamps_color" : new_stamp_color,
                                                                         "notes_color" : note_color}

    # Détails
    last_stamps = EnjoyTimestamp.objects.order_by("-published_date")[:5]





    context = {'hours' : [i for i in range(MIN_HOUR, MAX_HOUR)],
               'minutes' : [i for i in range(0, 60)],
               'nb_timestamps' : nb_timestamps,
               'timestamps_data' : json.dumps(timestamps_data),
               "default_stamp_color" : json.dumps(default_stamp_color),
               "default_note_color" : json.dumps(default_note_color),
               "last_stamps" : last_stamps,
                }
    

    return render(request, url, context)



@login_required
def enjoy_timeline_hour_minute(request, hour, minute):

    timestamps = EnjoyTimestamp.objects.filter(time__hour=hour).filter(time__minute=minute)
    mean_note = round(np.mean([timestamp.note for timestamp in timestamps if timestamp.note]), 2)
    mean_note = False if np.isnan(mean_note) else mean_note

    enjoy_form = EnjoyTimestampForm(request.POST or None)

    if enjoy_form.is_valid():
        instance = enjoy_form.save(commit=False)
        instance.published_date = now()
        instance.time = time(hour = hour, minute = minute)
        instance.writer = request.user
        instance.save()

        validate_objective_quest(user = request.user, action = "enjoy")

        return HttpResponseRedirect(f'/enjoy_timeline/{hour}/{minute}')
    
    if minute < 59:
        next_minute = minute + 1
        next_hour = hour
    else:
        next_minute = 0
        next_hour = hour + 1
        if next_hour == 24:
            next_hour = 0

    
    url = "Blog/enjoy_timeline/enjoy_timeline_hour_minute.html"
    context = {'hour' : hour,
               'minute' : minute,
               'next_hour' : next_hour,
               'next_minute' : next_minute,
               'timestamps' : timestamps,
               'form' : enjoy_form,
               'mean_note' : mean_note
    }


    return render(request, url, context)