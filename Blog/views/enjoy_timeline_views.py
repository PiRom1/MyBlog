

from django.contrib.auth.decorators import login_required
from django.utils import timezone
from Blog.models import EnjoyTimestamp, User
import json
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse


@login_required
def enjoy_timeline(request):

    url = "Blog/enjoy_timeline/enjoy_timeline.html"
    context = {}

    return render(request, url, context)