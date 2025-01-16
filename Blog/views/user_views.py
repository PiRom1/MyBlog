from django.shortcuts import render, redirect
from ..models import *
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from ..forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
import string
import re
import os

from ..utils.stats import *
import random as rd

from nltk.corpus import stopwords
import nltk
nltk.download('stopwords')
# Create your views here.


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
def UserView(request, id):
    
    user = request.user
    viewed_user = User.objects.filter(id = id)[0]

    # Condition si current user et viewed_user sont dans la même session
    session_user = [session.session_id for session in list(SessionUser.objects.filter(user_id=user.id))]
    session_viewed_user = [session.session_id for session in list(SessionUser.objects.filter(user_id=viewed_user.id))]
    
    messages = Message.objects.filter(writer=viewed_user)
    karma = messages.values_list('karma', flat=True)
    mean_karma = np.mean(karma)
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


    background_id = Skin.objects.get(type='background_image').id
    bg = UserInventory.objects.filter(item_id__item_id=background_id).filter(user=viewed_user).filter(equipped=True)
    if bg:
        bg = Background.objects.get(id=bg[0].item.pattern).image.url
    else:
        bg = None
    
    bot_ids = Bot.objects.all().values_list('user_id', flat=True)
    is_bot = viewed_user.id in bot_ids


    url = "Blog/user/user.html"
    context = {'viewed_user' : viewed_user,
               'n_messages' : n_messages,
               'form' : form,
               'messages' : messages,
               'words' : words,
               'plot' : plot,
               'user_bg' : bg,
               'is_bot' : is_bot,
               'mean_karma' : round(mean_karma, 2),
               }

    return render(request, url, context)



def update_plot(request):

    value = int(request.GET.get('value', 1))  # Obtention de la valeur du slider
    user = request.GET.get('user', 1)  # Obtention de la valeur du slider
    
    user = User.objects.get(username=user)
    messages = Message.objects.filter(writer=user)
    plot = get_messages_plot(messages, user, lissage = value)
    
    return JsonResponse({'plot': plot})
