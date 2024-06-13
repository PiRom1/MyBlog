from django.shortcuts import render
#from rest_framework import viewsets
from .models import Message
from django.http import HttpResponse, HttpResponseRedirect
from .forms import MessageForm, LoginForm, AddUserForm, ColorForm
from django.utils import timezone
from django.contrib.auth import authenticate, login, get_user
from django.contrib.auth.models import User
from django.db.models import F

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
            color = message_form['color'].value()
            #user = message_form['who']
            text = new_message.value()
            #user = user.get_username()
            #user = User.objects.filter(name = user)[0]
            print(text)
            new_message = Message(writer = user, text = text, pub_date = timezone.now(), color = color)  
            new_message.save()
            print(1)

    
    message_form = MessageForm()
    
    ### Get every dates : 
    years = []   # Contient les différentes années existantes
    month = []   # Contient les différents mois existants
    day = []   # Contient les différents jours existants
    dates = []

    when_new_date = []   # Liste de booléens. True si nouvelle date, False sinon. Permet de savoir quand on passe à un nouveau jour

    for message in Message.objects.all():
        message_date = str(message.pub_date).split()[0]
        message_date = message_date.split('-')

        dict = {'year' : message_date[0], 
                'month' : message_date[1],
                'day' : message_date[2]}
        
        months_num = {'01' : 'Janvier', '02' : 'Février', '03' : 'Mars', '04' : 'Avril' , '05' : 'Mai', '06' : 'juin',
                      '07' : 'Juillet', '08' : 'Août', '09' : 'Septembre', '10' : 'Octobre', '11' : 'Novembre', '12' : 'Décembre'}

        years.append(message_date[0])
        month.append(months_num[message_date[1]])
        day.append(message_date[2])

        if dict not in dates:
            when_new_date.append(True)
        else:
            when_new_date.append(False)
        
        dates.append(dict)






    context = {"messages" : messages, "MessageForm" : message_form, "user" : user, "years" : years, "month" : month, "day" : day, "when_new_date" : when_new_date}

    return render(request, "Blog/index.html", context)



def AddUser(request):

    add_user_form = AddUserForm(request.POST)

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



def upvote(request, message_id):
    
    message = Message.objects.filter(id = message_id)[0]
    message.upvote = F("upvote") + 1
    message.save()

    return HttpResponseRedirect("/")

def downvote(request, message_id):
    
    message = Message.objects.filter(id = message_id)[0]
    message.downvote = F("downvote") + 1
    message.save()

    return HttpResponseRedirect("/")

