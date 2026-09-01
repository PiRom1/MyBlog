import json
from django.shortcuts import render, redirect
from django.db import transaction

from ..models import *
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from ..forms import *
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.template.loader import render_to_string
from django.urls import reverse
import string
import re
from nltk.corpus import stopwords
import nltk
# nltk.download('stopwords')

from ..utils.process_text import process_text, ask_agent_question
from ..utils.llm_response import LLMResponse, LLMNewMessage

from ..utils.stats import *
import random as rd
from groq import Groq
from datetime import datetime
from Blog.views.utils_views import write_journal_tag
import os
from django.templatetags.static import static



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
    session_for_user = SessionUser.objects.filter(user = user, session = session).first()

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
            post_last_message_id = post_data['last_message_id']
            new_message = post_data['new_message']

            if rd.random() < 0.0005:
                response, username = LLMNewMessage(session)
                if response:
                    llm_user = User.objects.get(username=username)
                    new_message = Message(writer = llm_user, text = response, pub_date = timezone.now(), session_id = session, skin = '{}')
                    history = History(pub_date = timezone.now(), writer = llm_user, text = response, message = new_message)
                    new_message.save()
                    history.save()
                    last_message_id = new_message.id

            if int(post_last_message_id) < last_message_id:
                messages = Message.objects.filter(id__gt = post_last_message_id, session_id = session).order_by('-id')[:n_messages_par_page:-1]
                years, month, day, when_new_date = get_dates(messages)
                when_new_date = []
                post_last_message_id = last_message_id
            else:
                return JsonResponse({'messages_html': '',
                                     'last_message_id': post_last_message_id})
            
        
        messages_html = render_to_string('Blog/chat/messages.html', {
            'messages': messages,
            'user': user,
            'years': years,
            'month': month,
            'day': day,
            'when_new_date': when_new_date,
            'new_message': new_message})
        
        session_for_user.first_unseen_message = None
        session_for_user.unseen_messages_counter = 0
        session_for_user.save()

        
        return JsonResponse(data={'messages_html': messages_html,
                                  'last_message_id': messages[-1].id})

 # Get items
            
    items = UserInventory.objects.filter(user=request.user).filter(equipped=True)
    item_ids = [item.item.item_id for item in items]
    dict_items = {}

    for i,item_id in enumerate(item_ids):
        skin = Skin.objects.get(id=item_id).type
        dict_items[skin] = items[i].item.pattern
    if 'name_rgb' in dict_items and 'avatar_color' in dict_items:
        del dict_items['avatar_color']
    if 'border_image' in dict_items:
        dict_items['border_image'] = BorderImage.objects.get(name=dict_items['border_image']).image.url



    if request.method == "POST":
        # message_form = MessageForm(request.POST)
        message_text = request.POST.get('message_html')
        
        if message_text:

            # Journal
            for _user in User.objects.filter(sessionuser__session = session):
                if f"@{_user.username.lower()}" in message_text.lower():
                    write_journal_tag(writer = user,
                                      receiver = _user,
                                      session = session)
           
            # print("Before processing : \n", message_text)
            processed_message_text = process_text(message_text, user, session)
            # print("After processing : \n", processed_message_text)
            if not isinstance(processed_message_text, str):  # Si text est un HttpResponseRedirect
                return processed_message_text
            
            theo_last_message = Message.objects.filter(writer__username='theophile').last()

            new_message = Message(writer = user, text = processed_message_text, pub_date = timezone.now(), session_id = session, skin = str(dict_items))  
            history = History(pub_date = timezone.now(), writer = user, text = processed_message_text, message = new_message)

            new_message.save()
            history.save()
                    

            agent_called = ask_agent_question(message_text, session)
            # 1 chance sur 10 de déclencher une réponse de LLM
            if (user.username == 'theophile' and theo_last_message.pub_date < timezone.now() - timezone.timedelta(hours=12)) or rd.random() < 0.1 or agent_called:
                if agent_called:
                    response, username = LLMResponse(username = user.username, 
                                                     message = message_text, 
                                                     session = session, 
                                                     use_user_context = True, 
                                                     bot = agent_called)
                    print("Response bot : ", response, username)
                else:
                    response, username = LLMResponse(username = user.username, 
                                                     message = message_text, 
                                                     session = session)
                if response:
                    llm_user = User.objects.get(username=username)
                    new_message = Message(writer = llm_user, text = response, pub_date = timezone.now(), session_id = session, skin = "{}")
                    history = History(pub_date = timezone.now(), writer = llm_user, text = response, message = new_message)
                    new_message.save()
                    history.save()

                    while rd.random() < 0.1 :
                        allowed_bots = Bot.objects.filter(sessionbot__session=session).filter(can_answer=True).exclude(user__username=username.username)
                        if allowed_bots:
                            response, username = LLMResponse(username, response, session, rd.choice(allowed_bots))
                            if response:
                                llm_user = User.objects.get(username=username)
                                new_message = Message(writer = llm_user, text = response, pub_date = timezone.now(), session_id = session, skin = '{}')
                                history = History(pub_date = timezone.now(), writer = llm_user, text = response, message = new_message)
                                new_message.save()
                                history.save()
                    

            return HttpResponseRedirect('#bottom')

    # message_form = MessageForm()
    


    url = "Blog/chat/index.html"
    request.session['previous_url'] = request.get_full_path()
    
    vote = None
    sondage = Sondage.objects.filter(current=True).filter(session=session)
    choices = None
    if sondage:
        sondage = sondage[0]
        choices = list(SondageChoice.objects.filter(sondage=sondage))

    

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
    background = ''
    
    emoji_item_id = Skin.objects.get(type="emoji").id
    font_item_id = Skin.objects.get(type="font").id
    bg_item_id = Skin.objects.get(type="background_image").id
    
    for item in UserInventory.objects.filter(user=request.user):
        
        if item.item.item_id == emoji_item_id and item.item.pattern:
            emoji_id = item.item.pattern
            emoji = Emojis.objects.get(id=emoji_id)
            emojis.append(emoji)
        

        
        if item.item.item_id == font_item_id:
            favorite_fonts.append(item.item.pattern)
        
        if item.item.item_id == bg_item_id and item.equipped:
            background = Background.objects.get(id=item.item.pattern)
            background = background.image.url
            
    
    # Manage unseen_messages
    first_unseen_message = None or session_for_user.first_unseen_message
    session_for_user.unseen_messages_counter = 0
    session_for_user.first_unseen_message = None
    session_for_user.save()
    
    
    
    # Récupérer les 10 derniers opening logs
    
    opening_logs = OpeningLog.objects.filter(user_id__in=SessionUser.objects.filter(session=session).values('user')).order_by('-date')[:10]

    session_bots = SessionBot.objects.filter(session=session).values_list('bot__user__username', flat=True)    
    session_users = {user.username : {'url' : getattr(getattr(user.image, 'image', None), 'url', None),
                                      'is_bot' : user.username in session_bots}
                      for user in User.objects.filter(username__in=SessionUser.objects.filter(session=session).values('user__username'))}

    user_sounds = {us.sound.name: us.sound.sound.url
                   for us in UserSound.objects.filter(user=user).order_by('sound__name').select_related('sound')}
    user_sounds = {'Son aléatoire' : '', **user_sounds}

    pages = {
    'Accueil': reverse('get_session'),
    'Tickets': reverse('ticket_list'),
    'Sondages': reverse('sondage_list'),
    'Récits': reverse('recit_list'),
    'Inventaire': reverse('inventory'),
    'HDV': reverse('hdv'),
    'Jeux': reverse('list_jeux'),
    'Paris': reverse('list_paris'),
    'Quêtes': reverse('quest'),
    'DinoWars': reverse('user_dinos_view'),
    'Leaderboard': reverse('leaderboard_view'),
    'Atelier': reverse('atelier'),
    'Enjoy Timeline': reverse('enjoy_timeline'),
    'Stats': reverse('stats', args=[session.id]),
}


    is_quest_done = Quest.objects.filter(
        user=user,
        start_date__date=timezone.now().date(),
        achieved=True
    ).exists()

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
               "background" : background,
               "opening_logs": opening_logs,  # Ajout des opening logs
               "current_skins" : str(dict_items),
               "first_unseen_message" : first_unseen_message,
               "command_list" : json.dumps(['help', 'emoji', 'tag', 'bot', 'random', 'soundbox', 'kaomoji', 'page', 'get_diplodocoins']),
               "session_users" : json.dumps(session_users),
               'user_sounds' : json.dumps(user_sounds),
               'pages': json.dumps(pages),
               'is_quest_done': is_quest_done
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
    
    
    texts = ["Tu crois encore que ce bouton sert �� quelque chose ?",
             "Sérieux, arrête de cliquer, ça va t'amener nul part ... ",
             "T'es encore là ???",
             "Tu comptes cliquer encore longtemps ?",
             "T'es encore là ???",
             "À un moment il va falloir se trouver un vrai travail !",
             "J'en conclus que tu es probablement en intercontrat ...",
             "Je vais faire remonter à la direction que tu as du temps à perdre !",
             "Bon... Tu vas cliquer combien de fois encore ?",
             "Je n'ai rien à t'apprendre, je te promets !",
             "D'accord, je vois ... Monsieur cherche des easter eggs c'est cela ?",
             "Eh bien je suis désolé de t'apprendre que je n'en renferme aucun !",
             "Aucun, oui oui, tu m'as bien entendu !",
             "J'ai juste l'impression que tu me fais des attouchements là !",
             "Si tu as autant de temps à perdre, n'hésite pas à contribuer à Chat Acelys !",
             "Le GitHub est donné sur la page d'accueil !",
             "Tu ne vas donc jamais me lâcher les baskets ?",
             "Tu ne vas donc jamais me lâcher les baskets ?",
             "Tu ne vas donc jamais me lâcher les baskets ?",
             "Tu ne vas donc jamais me lâcher les baskets ?",
             "Tu ne vas donc jamais me lâcher les baskets ?",
             "Tu ne vas donc jamais me lâcher les baskets ?",
             "Tu ne vas donc jamais me lâcher les baskets ?",
             "Tu ne vas donc jamais me lâcher les baskets ?",
             "Tu ne vas donc jamais me lâcher les baskets ?",
             "Ah oui donc tu es quelqu'un de plutôt persistant !",
             "Me toucher dix fois pour avoir un nouveau message, il faut le faire !",
             "Tu as bien mérité un petit cadeau alors !",
             "Tends l'oreille, je vais te confier un secret ...",
             "Écoute attentivement",
]
    

    user = User.objects.get(username=request.user.username)
    counter = user.tkt_counter
    text = texts[counter]

    if counter < len(texts)-1:
        user.tkt_counter += 1
        user.save()


    return JsonResponse({'text' : text})



def ask_heure_enjoy(request):
    # Initialize Groq client with API key
    client = Groq(
        api_key = os.environ.get('GROQ_API_KEY')
    )
    bot = Bot.objects.get(user__username='enjoy')
    user = request.user
    prompt = f'''{bot.preprompt}.
                    {user.username} te demande l'heure. \n
                    Voici des informations sur {user.username} : {user.llm_context}. 
                    \nVoici l'heure exacte que tu dois donner : {datetime.now().hour} heures et {datetime.now().minute} minutes.
    '''
    
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": prompt
            },
        ],
        model=bot.model_name,
        temperature=bot.temperature,
        max_tokens=bot.max_tokens,
        top_p=bot.top_p,
        presence_penalty=bot.presence_penalty,
        frequency_penalty=bot.frequence_penalty
    )

    return JsonResponse({'message' : response.choices[0].message.content})


def chat_with_bot(request, id):
    message = ''
    answer = ''

    bot = Bot.objects.get(user_id=id)
    form = chatWithBotForm()

    if request.method == "POST":
        message = request.POST.get('message')
        use_user_context = request.POST.get('use_user_context')
        use_user_context = True if use_user_context else False
        answer, _ = LLMResponse(username = request.user.username, 
                                message = message, 
                                session = None, 
                                bot = bot, 
                                use_user_context = use_user_context)


        

    url = "Blog/chat/chat_with_bot.html"
    context = {"id": id,
               "bot" : bot,
               "image" : bot.user.image.image.url,
               "user" : bot.user,
               'form' : form,
               'message' : message,
               'answer' : answer}
    
    return render(request, url, context)


@transaction.atomic()
@login_required
def fraude(request):

    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return HttpResponseBadRequest('<h1>400 Bad Request</h1><p>Requête non autorisée.</p>')

    data = json.loads(request.body)

    try:
        user = User.objects.get(id = data.get('user_id'))
        session = Session.objects.get(id=data.get('session_id'))
        COIN_STR = f"<img src='{static('img/coin.png')}' width='20'>"

        nb_condamnations = user.nb_condamnations
        
        condamnation_texts = [
            f"L'utilisateur {user.username} s'est senti plus malin qu'un marsouin, et a tenté - vainement - de contourner le système pour s'en mettre plein les fouilles. Je vous mets en garde pour cette fois, mais la fois suivante vous écoperez d'une méchante peine d'amende en vertu de l'article 148-B du DiplodoCode Civil... À bon entendeur !",
            f"L'utilisateur {user.username} a été sanctionné pour tentative aggravée de détournement de fonds. Il est condamné, en vertu de l'article 148-B du DiplodoCode Civil, à verser la somme conséquente de {nb_condamnations} {COIN_STR} à la nation. C'était pas faute d'avoir prévenu ...",
            f"L'utilisateur {user.username} n'a apparemment pas compris que détourner de l'argent DiploPublique n'était pas une bonne chose ! Soit tu es l'enfant de Bernard Tapie, soit tu es complètement con ! Quoi qu'il en soit, je te condamne à verser {nb_condamnations} {COIN_STR} en vertu de l'article 148-B du DiplodoCode Civil.",
            f"L'utilisateur {user.username} a visiblement l'air d'avoir du temps et de l'argent à perdre. Grand bien lui fasse, je suis plus riche que lui, et dispose d'une infinité de temps ! En vertu de l'article 148-B du DiplodoCode Civil, je te retire {nb_condamnations} {COIN_STR}. À très bientôt, visiblement !",
            f"AVIS À LA COMMUNAUTÉ DIPLO --- L'utilisateur {user.username} est en réalité un riche mécène qui a décidé de financer le système DiploJudiciaire en simulant des détournements de fonds afin de payer des amendes en continu en vertu de l'article 148-B du DiplodoCode Civil. De fait, nous lui prélevons encore une fois {nb_condamnations} {COIN_STR}. <br>Cependant, nous tenons à l'informer que nous disposons d'une planche à billets infinie, et ne souffrons d'aucun système d'inflation (au contraire de lui, qui prend cher chaque jour de sa vie à voir sa piteuse fortune perdre en valeur jour après jour). <br>De fait, bien que cette action était vraiment bienvenue, nous invitons celui-ci à CESSER de payer des amendes pour le bien de son portefeuille.",
            f"L'utilisateur {user.username} en est donc à sa sixième tentative de fraude. À ce stade, ce n'est plus de la délinquance, c'est une vocation. Le tribunal a d'ailleurs ouvert un dossier RH à votre nom : malheureusement, le poste de `Fraudeur Diprofessionnel` n'est pas rémunéré, c'est même l'inverse, ce sera {nb_condamnations} {COIN_STR}, article 148-B du DiplodoCode Civil, vous commencez à le connaître je pense...",
            f"Fascinant. L'utilisateur {user.username} présente tous les symptômes du joueur compulsif : mauvaise gestion financière, comportements erratiques, impulsifs voire irrationnels... Mais si au casino vous pouvez parfois être gagnants, ici c'est nous les gagnants ! {nb_condamnations} {COIN_STR} vous serons prélevés, en vertu de l'article 148-B du DiplodoCode Civil",
            f"COMMUNIQUÉ OFFICIEL --- Le tribunal DiploJudiciaire informe la communauté que l'utilisateur {user.username} finance désormais À LUI SEUL la rénovation du palais de justice, la fontaine à eau du greffe et le pot de départ de la juge d'instruction. Nous le remercions chaleureusement de son don de {nb_condamnations} {COIN_STR} (article 148-B) et l'informons que la machine à café est encore en panne, au cas où il voudrait récidiver !",
            f"Le tribunal DiploJudiciaire s'est réuni en une assemblée exceptionnelle pour discuter au sujet de l'utilisateur {user.username}. Celui-ci a été unanime pour la première fois depuis plusieurs décennies : vous êtes complètement con. Malheureusement, si lors d'un meurtre, vous pourriez plaider la folie, aujourd'hui rien ne vous empêchera de payer les {nb_condamnations} {COIN_STR} demandées en vertu de l'article 148-B du DiplodoCode Civil.",
            f"Mauvaise nouvelle, {user.username} : si chez Action ou autre magasin de clochard dans lequel vous allez quotidiennement il existe des cartes de fidélité, l'article 148-B du DiplodoCode Judiciaire n'en prévoit aucune ! Ainsi, vous êtes encore et toujours condamné à verser {nb_condamnations} {COIN_STR} au tribunal !",
            f"L'utilisateur {user.username} se ... Hmm... Bon. Écoutez, je ne suis même plus en colère, je suis inquiet. Vous avez cliqué sur la même commande en sachant PERTINEMMENT ce qui allait se passer, et vous l'avez refait. Einstein appelait ça la folie. Moi j'appelle ça de la connerie. Il existe un numéro, c'est le {nb_condamnations}. Non, ce n'est pas un numéro à appeler pour aller mieux, c'est le nombre de {COIN_STR} d'amende que vous devez payer en vertu de l'article 148-B du DiplodoCode Civil.",
            f"BULLETIN MÉTÉO DIPLOJUDICIAIRE --- Ce jour : avis de tempête sur le portefeuille de l'utilisateur {user.username}, avec des rafales d'amendes atteignant les {nb_condamnations} {COIN_STR} (merci l'article 148-B). Les prévisions pour demain sont identiques, ainsi que celles d'après-demain, et ce jusqu'à ce que sa mère lui confisque son ordinateur...",
            f"Le tribunal tient à féliciter l'utilisateur {user.username} : grâce à son assiduité remarquable, l'article 148-B du DiplodoCode Civil est désormais l'article de loi le plus appliqué de toute l'histoire du droit DiploCivil. Cette contribution au patrimoine juridique lui coûtera {nb_condamnations} {COIN_STR}. L'Histoire retiendra son nom. Son banquier aussi.",
            f"ERRATUM --- Dans un précédent jugement, le tribunal avait qualifié l'utilisateur {user.username} de « complètement con ». Après réexamen approfondi du dossier et constatation de cette nouvelle tentative, le tribunal souhaite présenter ses excuses : le terme était très en-dessous de la réalité. La correction terminologique étant à la charge du demandeur, cela fera {nb_condamnations} {COIN_STR} en vertu de l'article 148-B, blablabla vous connaissez la chanson.",
            f"Le saviez-vous ? À chaque clic de l'utilisateur {user.username} sur cette commande, un stagiaire du greffe DiploJudiciaire doit remplir à la main le formulaire 148-B en trois exemplaires, les plastifier, puis les emmener dans 3 bureaux distincts à 3 étages différents. Il a des sacrées crampes, et commence sérieusement à fatiguer. Ah oui et surtout il vous déteste. La prochaine fois, pensez à lui. En attendant, payez vos {nb_condamnations} {COIN_STR} et laissez-le rentrer chez lui svp",
            f"OFFRE D'EMPLOI --- Le tribunal DiploJudiciaire recrute un psychologue spécialisé en comportements autodestructeurs. Le poste est intégralement financé par l'utilisateur {user.username}, qui vient encore de verser {nb_condamnations} {COIN_STR} au titre de l'article 148-B du DiplodoCode Civil. Le premier patient est déjà trouvé. Plotwist, c'est le financeur. La boucle est bouclée (avons-nous inventé le pitch du prochain Nolan ?).",
            f"Le tribunal a longuement hésité entre plusieurs qualifications juridiques pour cette énième tentative de l'utilisateur {user.username} : `acharnement procédurier carnassier`, `auto-flagellation pécuniaire`, ou notre préférée, `Folie fiscalo-destructrice`. Le DiplodoConseil constitutionnel tranchera. En attendant, l'article 148-B, lui, a déjà tranché : {nb_condamnations} {COIN_STR}.",
            f"MESSAGE PERSONNEL DU JUGE --- {user.username}, je vais être honnête avec vous. Ce matin, ma femme m'a demandé pourquoi je rentrais tard tous les soirs. Je lui ai parlé de vous. Elle ne m'a pas cru. `Personne n'est aussi bête`, m'a-t-elle dit. Alors ce soir, je lui apporte le dossier complet, merci d'avance au stagiaire qui va m'imprimer tout ça aujourd'hui ! Nous utiliserons vos {nb_condamnations} {COIN_STR} exigés par l'article 148-B pour payer les frais d'impression bien évidemment !",
            f"STATISTIQUE DU JOUR --- Selon l'Institut des DiploSondages, 100% des utilisateurs ayant cliqué {nb_condamnations + 1} fois sur cette commande s'appellent {user.username}. L'échantillon est certes réduit, mais la significativité est TOTALE. En vertu de l'article 148-B et de la loi des grands nombres (que vous financez), ce sera {nb_condamnations} {COIN_STR}.",
            f"Le tribunal informe l'utilisateur {user.username} qu'à ce niveau de récidive, l'article 148-B du DiplodoCode Civil ne suffit plus : nous avons dû créer POUR VOUS l'alinéa 148-B-bis, dit « clause {user.username} », qui stipule : « lorsqu'un utilisateur dépasse les limites de bienséance, le tribunal est autorisé à prélever {nb_condamnations} {COIN_STR} en soupirant très fort ». Félicitations, vous êtes entré dans la loi. Littéralement. Pour fêter cela, vous méritez bien cette médaille. Elle ne sert à rien et n'a aucune valeur. Remarquez, vous allez bien ensemble !",
            f"Le tribunal DiploJudiciaire est en restructuration interne afin de gérer la charge de travail plus que conséquente générée par la stupidité crasse de l'utilisateur {user.username}, abusant de l'article 148-B du DiplodoCode Civil. Nous reviendrons prochainement avec une organisation interne plus adaptée, qui évitera aux stagiaires de partir en burnout après 2 jours, l'inspection du travail nous ayant déjà donné plusieurs avertissements. Néanmoins, nous ne manquerons pas de vous prélever {nb_condamnations} {COIN_STR} pour la peine !"
        ]

        

        if nb_condamnations >= len(condamnation_texts): # Si on est arrivé au bout des messages
            condamnation_text = condamnation_texts[-1]
        else: # Sinon
            condamnation_text = condamnation_texts[nb_condamnations]

        user.coins -= nb_condamnations
        user.nb_condamnations += 1
        user.save()

        # Récompense ??
        if nb_condamnations == len(condamnation_texts) - 2: # Si on est à l'avant dernier message
            # L'utilisateur gagne un objet de quête
            medaille = Skin.objects.get(name = 'Médaille de la condamnation pour fraude DiploFiscale')
            item = Item.objects.create(type = 'skin',
                                        item_id = medaille.id)
            UserInventory.objects.create(user = user,
                                            item = item)

        juge = User.objects.get(username='juge')
        Message.objects.create(writer = juge, 
                               text = condamnation_text,
                               session_id = session,
                               skin = {'font' : 'Marcellus'})
        
        print(f"Utilisateur {user.username} condamné !")
        
    except Exception as e:
        print(f"Erreur lors du jugement de l'utilisateur {user.username}")
        print(e)



    return JsonResponse({'success' : True})