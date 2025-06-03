import json
from django.shortcuts import render, redirect

from Blog.models import *
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse

from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.template.loader import render_to_string



