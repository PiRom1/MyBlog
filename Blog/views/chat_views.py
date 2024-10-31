import json
from django.shortcuts import render, redirect

from ..models import *
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from ..forms import *
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.template.loader import render_to_string
import string
import re
from nltk.corpus import stopwords
import nltk
nltk.download('stopwords')

from ..utils.process_text import process_text

from ..utils.stats import *
import random as rd




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




@login_required
def Index(request, id):

    

    session = Session.objects.get(id = id)

    page_number = int(request.GET.get('page', 1))

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
            if int(last_message_id) < messages[-1].id:
                messages = Message.objects.filter(id__gt = last_message_id, session_id = session).order_by('-id')[:n_messages_par_page:-1]
                years, month, day, when_new_date = get_dates(messages)
                when_new_date = []
                last_message_id = messages[-1].id
            else:
                return JsonResponse({'messages_html': '',
                                     'last_message_id': last_message_id})
            
        messages_html = render_to_string('Blog/chat/messages.html', {
            'messages': messages,
            'user': user,
            'years': years,
            'month': month,
            'day': day,
            'when_new_date': when_new_date,
            'new_message': new_message})
        
        return JsonResponse(data={'messages_html': messages_html,
                                  'last_message_id': last_message_id})

    if request.method == "POST":
        # message_form = MessageForm(request.POST)
        message_text = request.POST.get('message_html')
        print("text : ", message_text)
        if message_text:
            print('valid !')

            # Get items
            items = UserInventory.objects.filter(user=request.user).filter(equipped=True)
            item_ids = [item.item.item_id for item in items]

            dict_items = {}

            for i,item_id in enumerate(item_ids):
                skin = Skin.objects.get(id=item_id).type
                dict_items[skin] = items[i].item.pattern
            if 'name_rgb' in dict_items and 'avatar_color' in dict_items:
                del dict_items['avatar_color']
            

            message_text = process_text(message_text, user, 'black', session)
            print("TEXTE : ", message_text)
            if not isinstance(message_text, str):  # Si text est un HttpResponseRedirect
                return message_text
            

            new_message = Message(writer = user, text = message_text, pub_date = timezone.now(), session_id = session, skin = str(dict_items))  
            history = History(pub_date = timezone.now(), writer = user, text = message_text, message = new_message)

            new_message.save()
            history.save()

            return HttpResponseRedirect('#bottom')

    # message_form = MessageForm()
    


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
    
    # yoda_path = os.path.join(settings.STATIC_ROOT, 'yoda') 
    # yoda_sounds = os.listdir(yoda_path)
    # yoda_sounds = [os.path.join('yoda', sound) for sound in yoda_sounds if sound.endswith('mp3')]


    yoda_sounds = list(UserSound.objects.filter(user=user))
    
    yoda_sounds = [sound.sound.sound.url for sound in yoda_sounds]
   

    # Get emojis and fonts
    emojis = []
    favorite_fonts = []

    
    emoji_item_id = Skin.objects.get(type="emoji").id
    font_item_id = Skin.objects.get(type="font").id
    
    for item in UserInventory.objects.filter(user=request.user):
        
        if item.item.item_id == emoji_item_id and item.item.pattern:
            emoji_id = item.item.pattern
            emoji = Emojis.objects.get(id=emoji_id)
            emojis.append(emoji.image.url)
        

        
        if item.item.item_id == font_item_id:
            favorite_fonts.append(item.item.pattern)
    
    
    

    
    
    
    context = {"messages" : messages, 
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
               "last_message_id" : last_message_id,
               "skins" : [message.skin for message in messages],
               "emojis" : emojis,
               "favorite_fonts" : favorite_fonts,
               }
    
    # rappel
    '''TYPE = [('text_color', 'Text color'), ('border_color', 'Border color'), ('avatar_color', 'Avatar color'),
            ('name_color', 'Name color'), ('background_color', 'Background color'), ('background_image', 'Background image'),
            ('font', 'Font'), ('emoji', 'Emoji'), ('border_image', 'Border image'),
            ('other', 'Other')]
    '''

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
