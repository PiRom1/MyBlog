import json
from django.shortcuts import render, redirect
#from rest_framework import viewsets
from .models import *
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.db.models import F
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.conf import settings
from django.templatetags.static import static
from django.template.loader import render_to_string
import string
import re
import os
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
nltk.download('stopwords')
from nltk.stem.snowball import FrenchStemmer

from .utils.process_text import process_text

from .utils.stats import *
import random as rd
import bleach


def can_access(user, viewed_user): 
    
    # Condition si current user et viewed_user sont dans la même session
    session_user = [session.session_id for session in list(SessionUser.objects.filter(user_id=user.id))]
    session_viewed_user = [session.session_id for session in list(SessionUser.objects.filter(user_id=viewed_user.id))]
    
    access = False

    for user_id in session_user:
        if user_id in session_viewed_user:
            access = True

    return access


def normalize_answer(s):
    """Lower text and remove punctuation, articles and extra whitespace."""
    def remove_articles(text):
        regex = stopwords.words('french')
        regex = re.compile(r'\b({})\b'.format('|'.join(regex)))
        return re.sub(regex, ' ', text)
    def white_space_fix(text):
        return ' '.join(text.split())
    def remove_punc(text):
        text = text.replace("'", " ")  # Remplacement apostrophe par espace
        exclude = set(string.punctuation)
        return ''.join(ch for ch in text if ch not in exclude)
    def lower(text):
        return text.lower()
    def accents(text):
        accents = [('é','e'), ('è','e'), ('à', 'a'), ('ù', 'u'), ('ê', 'e'), ('ô', 'o'), ('î', 'i'), ('ï', 'i'), ('ë', 'e'), ('â', 'a'), ('û', 'u'), ('ü', 'u'), ('ç', 'c')]
        for accent in accents:
            text = text.replace(accent[0], accent[1])
        return text
    
    return white_space_fix(accents(remove_articles(remove_punc(lower(s)))))

def get_tokens(s):
  if not s: return [""]
  rep = normalize_answer(s).split()
  return rep if rep!=[] else [""]

def get_dates(messages):
    ### Get every dates : 
    years = []   # Contient les différentes années existantes
    month = []   # Contient les différents mois existants
    day = []   # Contient les différents jours existants
    dates = []
    when_new_date = []   # Liste de booléens. True si nouvelle date, False sinon. Permet de savoir quand on passe à un nouveau jour

    for message in messages:
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
            dates.append(dict)
        else:
            when_new_date.append(False)
        

    return years, month, day, when_new_date




# Create your views here.

def connexion(request):
    deconnexion(request)
    print("Connexion ...")
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

@login_required
def deconnexion(request):
    
    print("Logging out ... ")
    
    logout(request)
    return HttpResponseRedirect("/login/")

def InvalidUser(request):
    context =  {}
    return render(request, "Blog/invalid_user.html", context)

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


@login_required
def Index(request, id):

    session = Session.objects.get(id = id)

    page_number = int(request.GET.get('page', 1))
    print(page_number)

    n_messages_par_page = 20
    messages = Message.objects.filter(session_id=session).order_by('-id')[:n_messages_par_page*page_number:-1]

    user = request.user

    # Vérification de l'autorisation d'accès
    if not SessionUser.objects.get(user = user, session = session):
        return HttpResponseRedirect("/invalid_user/")
    
    years, month, day, when_new_date = get_dates(messages)

    last_message_id = messages[-1].id if messages else 0

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        new_message = True
        # Si la requête est une requête AJAX, on retourne les messages sous forme de JSON 
        if request.method == "POST":
            post_data = json.loads(request.body.decode("utf-8"))
            last_message_id = post_data['last_message_id']
            new_message = post_data['new_message']
            print(last_message_id)
            print(new_message)
            if int(last_message_id) < messages[-1].id:
                messages = Message.objects.filter(id__gt = last_message_id, session_id = session).order_by('-id')[:n_messages_par_page:-1]
                years, month, day, when_new_date = get_dates(messages)
                when_new_date = []
                last_message_id = messages[-1].id
            else:
                return JsonResponse({'messages_html': '',
                                     'last_message_id': last_message_id})

        print(messages)            
            
        messages_html = render_to_string('Blog\chat\messages_inexistants.html', {
            'messages': messages,
            'user': user,
            'years': years,
            'month': month,
            'day': day,
            'when_new_date': when_new_date,
            'new_message': new_message})
        
        print(messages_html)
        
        return JsonResponse(data={'messages_html': messages_html,
                                  'last_message_id': last_message_id})

    if request.method == "POST":
        message_form = MessageForm(request.POST)

        if message_form.is_valid():
            new_message = message_form['message']
            color = message_form['color'].value()
            #user = message_form['who']
            text = new_message.value()

            text = process_text(text, user, color, session)

            if not isinstance(text, str):  # Si text est un HttpResponseRedirect
                return text

            new_message = Message(writer = user, text = text, pub_date = timezone.now(), color = color, session_id = session)  
            history = History(pub_date = timezone.now(), writer = user, text = text, message = new_message)

            new_message.save()
            history.save()

            return HttpResponseRedirect('#bottom')

    message_form = MessageForm()
    


    url = "Blog/chat/index.html"

    sondage = Sondage.objects.filter(current=True)
    choices = None
    if sondage:
        sondage = sondage[0]
        choices = list(SondageChoice.objects.filter(sondage=sondage))

    request.session['previous_url'] = request.get_full_path()

    user_choices = ChoiceUser.objects.filter(user_id=user.id)

    vote = None

    # Detect user cote
    for user_choice in user_choices:
        for choice in choices:
            if user_choice.choice_id == choice.id:
                vote = choice
    
    yoda_path = os.path.join(settings.STATIC_ROOT, 'yoda') 
    yoda_sounds = os.listdir(yoda_path)
    yoda_sounds = [os.path.join('yoda', sound) for sound in yoda_sounds if sound.endswith('mp3')]
 
    context = {"messages" : messages, 
               "MessageForm" : message_form, 
               "user" : user, "years" : years, 
               "month" : month, "day" : day, 
               "when_new_date" : when_new_date,
               "session" : session,
               "sondage" : sondage,
               "choices" : choices,
               "vote" : vote,
               "page_number" : page_number,
               "page_number_next" : page_number+1,
               "yoda_sounds" : yoda_sounds,
               "last_message_id" : last_message_id
               }

    return render(request, url, context)



@login_required
def IndexUser(request, id):
    

    viewed_user = User.objects.get(id = id)
    user = request.user
    user.is_authenticated

    if not can_access(user, viewed_user):
        return HttpResponseRedirect("/invalid_user/")
    
    messages = Message.objects.filter(writer=viewed_user)

    years, month, day, when_new_date = get_dates(messages)

    url = "Blog/chat/index_user.html"

    context = {"messages" : messages, 
               "viewed_user" : viewed_user,
               "user" : user, "years" : years, 
               "month" : month, "day" : day, 
               "when_new_date" : when_new_date,
               }

    return render(request, url, context)

@login_required
def IndexUserMessage(request, id, word):
    

    viewed_user = User.objects.get(id = id)
    user = request.user
    user.is_authenticated

    if not can_access(user, viewed_user):
        return HttpResponseRedirect("/invalid_user/")
    
    messages = list(Message.objects.filter(writer=viewed_user))
   
    messages = [message for message in messages if word in get_tokens(message.text)]
    
    years, month, day, when_new_date = get_dates(messages)
   
    url = "Blog/chat/index_user.html"

    context = {"messages" : messages, 
               "viewed_user" : viewed_user,
               "user" : user, "years" : years, 
               "month" : month, "day" : day, 
               "when_new_date" : when_new_date,
               "word" : word
               }

    return render(request, url, context)



@login_required
def ticket_list(request):
    tickets = Ticket.objects.all()
    open_tickets = tickets.filter(status='open')
    closed_tickets = tickets.filter(status='closed')
    in_progress_tickets = tickets.filter(status='in_progress')
    print(tickets)
    print(open_tickets)
    return render(request, 'Blog/tickets/ticket_list.html', {'tickets': tickets,
                                                             'open_tickets': open_tickets,
                                                             'closed_tickets': closed_tickets,
                                                             'in_progress_tickets': in_progress_tickets})

@login_required
def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()

            subject = 'Nouveau ticket : ' + ticket.title
            email_from = settings.EMAIL_HOST_USER
            if ticket.assigned_to and ticket.assigned_to.email:
                recipient_list = [ticket.assigned_to.email, ]
                message = f"""Hey {ticket.assigned_to.username},\n\n
                            Un nouveau ticket t\'a été assigné par {ticket.created_by.username} !\n
                            Tu peux le consulter à l'adresse suivante : https://diplo.pythonanywhere.com/tickets/update/{ticket.id}/"""
            elif ticket.created_by.email:
                recipient_list = [ticket.created_by.email, ]
                message = f'Hey {ticket.created_by.username}, malheureusement la personne à qui tu as assigné le ticket n\'a pas d\'adresse mail valide.'
            else:
                return redirect('ticket_list')
            send_mail( subject, message, email_from, recipient_list )

            return redirect('ticket_list')
    else:
        form = TicketForm()
        # préremplir le champ titre avec le texte du dernier message si il commence par "Nouveau ticket :"
        last_message = Message.objects.last()
        code = (last_message.text.split(':')[0]).lower().strip()
        if code == "nouveauticket":
            form.fields['title'].initial = last_message.text.split(':',1)[1]
            last_message.delete()
    return render(request, 'Blog/tickets/create_ticket.html', {'form': form})

@login_required
def update_ticket(request, pk):
    ticket = Ticket.objects.get(pk=pk)
    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('ticket_list')
    else:
        form = TicketForm(instance=ticket)
    return render(request, 'Blog/tickets/update_ticket.html', {'form': form, 'ticket': ticket})


@login_required
def change_photo(request):
    
    user = request.user

    photo_form = PhotoForm(request.POST, request.FILES)
    photo = None

    print(photo_form.is_valid())

    if request.method == "POST":

        if photo_form.is_valid():
                
            photo = photo_form.cleaned_data['photo']
            

            photo = Photo(image = photo)
            photo.save()
            
            user.image = photo

            user.save()
        
           


    url = "Blog/user/change_photo.html"

    context = {"user" : user,
               "form" : photo_form,
               "photo" : photo
               }

    return render(request, url, context)



@login_required
def Stats(request, id):

    user = request.user
    session = Session.objects.get(id = id)


    if not SessionUser.objects.get(user = user, session = session):
        return HttpResponseRedirect("/invalid_user/")

    
    message_stats, yoda_stats, enjoy_stats = get_stats(session)

    print(message_stats)
    print(yoda_stats)

    url = "Blog/chat/stats.html"
    context = {"message_stats" : message_stats,
               "yoda_stats" : yoda_stats,
               "enjoy_stats" : enjoy_stats,
               "session" : session}

    return render(request, url, context)


@login_required
def UserView(request, id):
    
    user = request.user
    viewed_user = User.objects.filter(id = id)[0]

    # Condition si current user et viewed_user sont dans la même session
    session_user = [session.session_id for session in list(SessionUser.objects.filter(user_id=user.id))]
    session_viewed_user = [session.session_id for session in list(SessionUser.objects.filter(user_id=viewed_user.id))]
    
    messages = Message.objects.filter(writer=viewed_user)
    n_messages = len(messages)

    messages = ' '.join([message.text for message in messages])
    messages = get_tokens(messages)
    messages = ' '.join(messages)
    messages = messages.lower()
    messages = messages.split()
    words = list(set(messages))
    w = words.copy()
    for word in w:
        if len(word) < 5:
            words.remove(word)
    count_words = {}

    

    for word in words:
        count_words[word] = messages.count(word)
    
    n_max = 0

    words = list(count_words.keys())
    nb = list(count_words.values())

    argsorts = np.argsort(nb)[-1: -6: -1]

    words = np.array(words)[argsorts]
    nb = np.array(nb)[argsorts]
    
    words = zip(words, nb)
    

    access = False

    for user_id in session_user:
        if user_id in session_viewed_user:
            access = True

    if not access:
        return HttpResponseRedirect("/invalid_user/")

    form = ModifyUserForm(initial={'last_name' : user.last_name,
                                   'first_name' : user.first_name,
                                   'email' : user.email})
    if request.method == 'POST':

        form = ModifyUserForm(request.POST)
        
        if form.is_valid():
            
            data = form.data            
            first_name = data['first_name']
            last_name = data['last_name']
            email = data['email']

            user.first_name = first_name
            user.last_name = last_name
            user.email = email

            user.save()

            return HttpResponseRedirect('.')

        


    messages = Message.objects.filter(writer=viewed_user)

    plot = get_messages_plot(messages, viewed_user)



    url = "Blog/user/user.html"
    context = {'viewed_user' : viewed_user,
               'n_messages' : n_messages,
               'form' : form,
               'messages' : messages,
               'words' : words,
               'plot' : plot,
               }

    return render(request, url, context)


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
def recit_list(request):
    recits = Recit.objects.all()
    nb_textes = []

    for recit in recits:
        texte = Texte.objects.filter(recit=recit)
        nb_textes.append(len(texte))
    

    context = {'recits' : zip(recits, nb_textes),
               }
    
    return render(request, 'Blog/recits/recit_list.html', context)

@login_required
def create_recit(request):
        
    if request.method == "POST":
        message_form = CharForm(request.POST)

        if message_form.is_valid():
            new_recit = Recit(name = message_form['message'].value())
            new_recit.save()

            return HttpResponseRedirect(f"/recits/detail/{new_recit.id}")
    
    message_form = CharForm()

    context = {'form' : message_form,
    }
    
    return render(request, 'Blog/recits/create_recit.html', context)


@login_required
def detail_recit(request, pk):
    
    recit = Recit.objects.get(pk=pk)
    texts = Texte.objects.filter(recit = recit)
    user = request.user

    if request.method == 'POST':
        form = MessageForm2(request.POST)

        if form.is_valid():

            texte = form['message'].value()
            texte = Texte(text = texte, user = user, recit = recit)
            texte.save()

            return HttpResponseRedirect('.#bottom')
    
    form = MessageForm2()

    if not texts:
        is_last_writer = False
    else:
        is_last_writer = list(texts)[-1].user == user
    
    
    print(is_last_writer)
    context = {'form' : form, 
               'recit' : recit,
               'texts' : texts,
               'is_last_writer' : is_last_writer}
    
    return render(request, 'Blog/recits/detail_recit.html', context)




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


def increment_yoda(request):
    if request.method == 'POST':
        user = request.user  # Récupérer l'objet
        user.yoda_counter += 1  # Incrémenter le compteur
        user.save()  # Sauvegarder en base
        return JsonResponse({'status': 'ok', 'new_value': user.yoda_counter})



def increment_enjoy(request):
    if request.method == 'POST':
        user = request.user  # Récupérer l'objet
        user.enjoy_counter += 1  # Incrémenter le compteur
        user.save()  # Sauvegarder en base
        return JsonResponse({'status': 'ok', 'new_value': user.enjoy_counter})


def tkt_view(request):
    print('ici')
    
    texts = ["Je ramène les chocolatines demain !", 
                "Je ramène plein de croissants demain matin !", 
                "Je vous invite au restau ce midi les p'tits potes, ça me fait plaisir :)",
                "Les gars demain matin c'est moi qui ramène le p'tit dèj ;)",
                ]
    print(175)

    session_id = request.GET.get('session')
    session = Session.objects.get(id=session_id)
    message = Message(writer = request.user, text = rd.choice(texts), pub_date = timezone.now(), color = 'black', session_id = session)  
    message.save()

    return HttpResponseRedirect(f'/{session_id}#bottom')


def update_plot(request):

    value = int(request.GET.get('value', 1))  # Obtention de la valeur du slider
    print(value)
    user = request.user
    messages = Message.objects.filter(writer=user)
    plot = get_messages_plot(messages, user, lissage = value)
    #print(plot)
    return JsonResponse({'plot': plot})



# def Modify(request, message_id):
#     message = Message.objects.filter(id = message_id)[0]
#     history_message = History.objects.filter(message = message)
#     user = request.user
#     user.is_authenticated
#     print(type(user))
#     print(user)
#     if request.method == "POST":
#         modify_form = ModifyForm(request.POST)
#         modification = modify_form['modify']
#         message.text = modification.value()
#         message.save()
#         history = History(pub_date = timezone.now(), writer = message.writer, text = modification.value(), message = message)
#         history.save()

#         return HttpResponseRedirect("/")

#     else:
#         modify_form = ModifyForm()

#     context = {"message" : message, "form" : modify_form, 'history_message' : history_message}
               
#     return render(request, "Blog/chat/modify.html", context)
    

# def AddUser(request):

#     add_user_form = AddUserForm(request.POST)

#     if add_user_form.is_valid():
#         username = add_user_form['username'].value()
#         password = add_user_form['password'].value()

#         user = User.objects.create_user(username = username, password = password)
#         user = authenticate(request, username=username, password=password)
#         login(request, user)
#         print(user)

#         return HttpResponseRedirect("/")
    
#     context = {"add_user_form" : add_user_form}

#     return(render(request, "Blog/user/AddUser.html", context))

# def dark_mode(request):
#     user = get_user(request)
#     user.is_authenticated
#     print("User : ", user.is_staff)
#     user.is_staff = 1 - user.is_staff
#     user.save()
#     return HttpResponseRedirect('/')



# def upvote(request, message_id):
    
#     message = Message.objects.filter(id = message_id)[0]
#     message.upvote = F("upvote") + 1
#     message.save()

#     return HttpResponseRedirect("/")

# def downvote(request, message_id):
    
#     message = Message.objects.filter(id = message_id)[0]
#     message.downvote = F("downvote") + 1
#     message.save()

#     return HttpResponseRedirect("/")

