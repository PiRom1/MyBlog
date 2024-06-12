from django.shortcuts import render
#from rest_framework import viewsets
from .models import Message
from django.http import HttpResponse, HttpResponseRedirect
from .forms import MessageForm, LoginForm
from django.utils import timezone
from django.contrib.auth import authenticate, login, get_user
from django.contrib.auth.models import User

# Create your views here.



def Index(request):
    """
    API Endpoint that shows overall data of the conformity percentage
    specific regulation data can be accessed with by passing the regulation id in the url parameters
    """
    messages = Message.objects.all()
    user = get_user(request)
    user.is_authenticated
    print(type(user))
    print(user)

    if request.method == "POST":
        message_form = MessageForm(request.POST)

        if message_form.is_valid():
            new_message = message_form['message']
            #user = message_form['who']
            text = new_message.value()
            #user = user.get_username()
            #user = User.objects.filter(name = user)[0]
            print(text)
            new_message = Message(writer = user, text = text, pub_date = timezone.now())  
            new_message.save()
            print(1)

    
    message_form = MessageForm()
    


    context = {"messages" : messages, "MessageForm" : message_form, "user" : user}

    return render(request, "Blog/index.html", context)



def AddUser(request):

    add_user_form = LoginForm(request.POST)

    if add_user_form.is_valid():
        username = add_user_form['username'].value()
        password = add_user_form['password'].value()

        user = User.objects.create_user(username = username, password = password)
        user = authenticate(request, username=username, password=password)
        login(request, user)
        print(user)

        return HttpResponseRedirect("/")
    
    context = {"add_user_form" : add_user_form}

    return(render(request, "Blog/AddUser.html", context))





def connexion(request):

    login_form = LoginForm(request.POST)
    
    if login_form.is_valid():
        username = login_form['username'].value()
        password = login_form['password'].value()

        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
            print(user)
            return HttpResponseRedirect("/")
    
    else:
        login_form = LoginForm()
    
    context = {"login_form" : login_form}




    return(render(request, "Blog/connexion.html", context))

