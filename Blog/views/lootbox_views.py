from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required



@login_required
def open_lootbox(request):
    url = 'Blog/lootbox/openning.html'
    return render(request, url)