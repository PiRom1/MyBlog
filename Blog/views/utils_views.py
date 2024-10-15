from django.shortcuts import render, redirect

from ..models import *
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from ..forms import *
from django.contrib.auth.decorators import login_required

from ..utils.stats import *
import random as rd



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