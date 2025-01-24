

from django.contrib.auth.decorators import login_required
from django.utils import timezone
from Blog.models import EnjoyTimestamp, User
from Blog.forms import EnjoyTimestampForm
from django.db.models.functions import ExtractHour, ExtractMinute
from django.db.models import Count
import json
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
import numpy as np
from datetime import datetime, time
from django.utils.timezone import now

@login_required
def enjoy_timeline(request):

    url = "Blog/enjoy_timeline/enjoy_timeline.html"

    hours =  [i for i in range(9, 19)]
    minutes = [i for i in range(0, 60)]

    import numpy as np

    timestamps = EnjoyTimestamp.objects.annotate(
    hour=ExtractHour('time'), 
    minute=ExtractMinute('time')).values('hour', 'minute').annotate(count=Count('id')).order_by('hour', 'minute')

    timestamps = list(timestamps)
    values = [i['count'] for i in timestamps]

    scale = 400
    
    if values:
        max_timestamps = max(max(values), 1)
        min_timestamps = max(min(values), 1)
    else:
        max_timestamps = 1
        min_timestamps = 1

    ecart = max_timestamps - min_timestamps + 2
    scale_table = [(i+1)*scale/ecart for i in range(ecart-1)]

    

    timestamps_dict = {}
    for timestamp in timestamps:
        timestamps_dict[f"{timestamp['hour']}_{timestamp['minute']}"] = timestamp['count']
    
    print(min_timestamps, max_timestamps)
    nb = {}
    colors = {}

    for hour in hours:
        for minute in minutes:
            nb_timestamps = timestamps_dict.get(f"{hour}_{minute}")
            nb_timestamps = nb_timestamps if nb_timestamps else 0
            if nb_timestamps == 0:
                new_color = [200, 200, 200]
            else:
                color = scale_table[nb_timestamps-1]
                if color <= 220 : 
                    new_color = [255, 220-color, 220-color]
                else:
                    color = color - 220
                    new_color = [255-color, 0, 0]

            nb[f"{hour}_{minute}"] = nb_timestamps
            colors[f"{hour}_{minute}"] = new_color
    
    

    context = {'hours' : [i for i in range(9, 19)],
               'minutes' : [i for i in range(0, 60)],
               'nb' : nb,
               'colors' : colors,
                }

    return render(request, url, context)



@login_required
def enjoy_timeline_hour_minute(request, hour, minute):

    timestamps = EnjoyTimestamp.objects.filter(time__hour=hour).filter(time__minute=minute)

    enjoy_form = EnjoyTimestampForm(request.POST or None)

    if enjoy_form.is_valid():
        instance = enjoy_form.save(commit=False)
        instance.published_date = now()
        instance.time = time(hour = hour, minute = minute)
        instance.writer = request.user
        instance.save()

        return HttpResponseRedirect(f'/enjoy_timeline/{hour}/{minute}')
    
        
    url = "Blog/enjoy_timeline/enjoy_timeline_hour_minute.html"
    context = {'hour' : hour,
               'minute' : minute,
               'timestamps' : timestamps,
               'form' : enjoy_form,
    }

    return render(request, url, context)