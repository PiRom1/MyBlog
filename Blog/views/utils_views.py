from django.shortcuts import render, redirect

from ..models import *
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from ..forms import *
from django.contrib.auth.decorators import login_required

from ..utils.stats import *
import random as rd
import json



@login_required
def getSession(request):
    
    user = request.user
    connecte = user.is_authenticated

    if not connecte:
        return HttpResponseRedirect("/login/")

    session_data = [{"session" : session_for_user.session,
                     "nb_unseen_messages" : session_for_user.unseen_messages_counter} for session_for_user in SessionUser.objects.filter(user=user)]

    context = {"session_data" : session_data, "user" : user}
    return render(request, "Blog/get_session.html", context)


@login_required
def getSession_v2(request):
    
    user = request.user
    connecte = user.is_authenticated

    if not connecte:
        return HttpResponseRedirect("/login/")

    session_data = [{"session" : session_for_user.session,
                     "nb_unseen_messages" : session_for_user.unseen_messages_counter} for session_for_user in SessionUser.objects.filter(user=user)]

    # Les catégories, sous catégories, textes à afficher et liens où rediriger
    # Ex : [
    #        {'category' : 'Sessions', 
    #         'subcategory' : [
    #                             {'name' : 'Chat Acelys (+5), 
    #                              'link' : 'https://...'},
    #                         ],
    #         },
    #      ]

    # Catégories : Sessions, Objets, Jeux, Réclamations, Autres ??? À définir
    categories = [{"category" : "Objets & Progression", "subcategory" : [{"name" : "Inventaire", "link" : "/inventory/"},
                                                                         {"name" : "Hôtel des ventes", "link" : "/hdv"},
                                                                         {"name" : "Atelier", "link" : "/atelier/"},
                                                                         {"name" : "Quêtes", "link" : "/quêtes/"}]},
                  {"category" : "Compte", "subcategory" : [{"name" : "Profil", "link" : f"/user/{user.id}/"},
                                                           {"name" : "Changer sa photo de profil", "link" : "/change_photo"},
                                                           {"name" : "Déconnexion", "link" : "/logout/"},]},
                  {"category" : "Collaboration & Support", "subcategory" : [{"name" : "Tickets", "link" : "/tickets/"},
                                                                            {"name" : "Sondages", "link" : "/sondages/"},
                                                                            {"name" : "Récits", "link" : "/recits/"},
                                                                            {"name" : "Timeline Enjoy", "link" : "/enjoy_timeline"},
                                                                            {"name" : "Soundbox", "link" : "/list_sounds"},
                                                                            {"name" : "Soundbox", "link" : "/list_sounds"},
                                                                            {"name" : "Soundbox", "link" : "/list_sounds"},
                                                                            {"name" : "Soundbox", "link" : "/list_sounds"},
                                                                            {"name" : "Soundbox", "link" : "/list_sounds"},
                                                                            {"name" : "GitHub", "link" : "https://github.com/PiRom1/MyBlog"}]},
                  {"category" : "Jeux", "subcategory" : [{"name" : "DinoWars", "link" : "/dinowars/"},
                                                         {"name" : "Salle de jeux", "link" : "/jeux/"},
                                                         {"name" : "Paris", "link" : "/paris/"}]}
                ]
    
    
    session_data = []
    for session_for_user in SessionUser.objects.filter(user=user):
        nb_unseen_messages = session_for_user.unseen_messages_counter
        session_name = session_for_user.session.session_name
        link = f"/{session_for_user.session.id}/#bottom"
        if nb_unseen_messages >= 1:
            session_name += f" (+{nb_unseen_messages})"
        
        session_data.append({"name" : session_name,
                             "link" : link})

    categories.insert(0, {"category" : "Sessions", "subcategory" : session_data})


    context = {"categories" : json.dumps(categories), "user" : user.username.capitalize()}
    return render(request, "Blog/get_session_v2.html", context)



@login_required
def get_moderaptor(request):
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return HttpResponseBadRequest('<h1>400 Bad Request</h1><p>Requête non autorisée.</p>')
    
    response = {'success' : True, 'log' : 'You got Moderaptor. Enjoy !'}

    print('repsonse : ', response)
    return JsonResponse(response)




def get_random_hexa_color():
    caracs = [str(i) for i in range(10)] + ['A', 'B', 'C', 'D', 'E', 'F']
    choices = rd.choices(caracs, k = 3)
    return '#' + ''.join(choices)

def get_random_animated_color():
    caracs = ['#F00','#F80','#FF0','#8F0','#090','#0F8','#0FF','#08F','#00F','#80F','#F0F','#F08','#000','rainbow']
    return rd.choice(caracs)


def get_item(skin_id):

    # Instantiate new item
    skin = Skin.objects.get(id=skin_id)

    if skin.type == 'font':
        item = Item(type='skin',
                    pattern=Font.objects.get(id=rd.randint(1,1112)).name,
                    item_id=skin_id)
    elif skin.type == 'emoji' or skin.type == 'background_image':
        item = Item(type='skin',
                    pattern='',
                    item_id=skin_id)
    # Il manque Border image
    elif skin.type == 'border_rgb' or skin.type == 'name_rgb':
        item = Item(type='skin',
                    pattern=get_random_animated_color(),
                    item_id=skin_id)
    elif skin.type == 'border_image':
        border_images = BorderImage.objects.all().values_list('name', flat=True)
        item = Item(type='skin',
                    pattern = rd.choice(border_images),
                    item_id=skin_id)
    else:
        item = Item(type='skin',
                    pattern=get_random_hexa_color(),
                    item_id=skin_id)
    

    return item, skin



DIPLODOCOIN_STR = "pièces " #"<img src='{% static 'img/coin.png' %}' width='20'> "



def write_journal_soundbox_add(user, sound):

    for _user in User.objects.all():

        if user != _user:
            entry = f"{user.username} a ajouté le son '{sound.name}' à la soundbox"

            JournalEntry.objects.create(entry_type = JournalEntryType.objects.get(entry_type = 'Soundbox'),
                                        user = _user,
                                        entry = entry)


def write_journal_sondage_create(user, sondage):

    session_users = User.objects.filter(sessionuser__session=sondage.session)

    for _user in session_users:

        if user != _user:
            entry = f"{user.username} a créé le sondage '{sondage.question}' dans la session {sondage.session.session_name}"

            JournalEntry.objects.create(entry_type = JournalEntryType.objects.get(entry_type = 'Sondage'),
                                        user = _user,
                                        entry = entry)



def write_journal_recit_create(user, recit):

    for _user in User.objects.all():

        if user != _user:
            entry = f"{user.username} a créé le récit '{recit.name}'"

            JournalEntry.objects.create(entry_type = JournalEntryType.objects.get(entry_type = 'Récit'),
                                        user = _user,
                                        entry = entry)



def write_journal_recit_contribute(user, recit):

    users = User.objects.filter(texte__recit=recit).distinct()

    for _user in users:

        if _user != user:

            entry = f"{user.username} a contribué au récit '{recit.name}'"

            JournalEntry.objects.create(entry_type = JournalEntryType.objects.get(entry_type = 'Récit'),
                                        user = _user,
                                        entry = entry)



def write_journal_ticket_create(user, ticket):

    for _user in User.objects.all():

        if user != _user:

            entry = f"{user.username} a créé le ticket '{ticket.title}'"
            JournalEntry.objects.create(entry_type = JournalEntryType.objects.get(entry_type = 'Ticket'),
                                        user = _user,
                                        entry = entry)



def write_journal_ticket_update(user, ticket):

    for _user in User.objects.all():

        if user != _user:

            entry = f"{user.username} a modifié le ticket '{ticket.title}'"
            JournalEntry.objects.create(entry_type = JournalEntryType.objects.get(entry_type = 'Ticket'),
                                        user = _user,
                                        entry = entry)



def write_journal_quest_new():

    for user in User.objects.all():

        entry = "Deux nouvelles quêtes sont disponibles"
        JournalEntry.objects.create(entry_type = JournalEntryType.objects.get(entry_type = 'Quête'),
                                        user = user,
                                        entry = entry)



def write_journal_pari_create(user, pari):

    for _user in User.objects.all():

        if user != _user:

            entry = f"{user.username} a créé le pari '{pari.name}'"
            JournalEntry.objects.create(entry_type = JournalEntryType.objects.get(entry_type = 'Pari'),
                                        user = _user,
                                        entry = entry)



def write_journal_pari_bet(user, pari, user_for_issue):

    pari_issues = PariIssue.objects.filter(pari = pari)
    users = User.objects.filter(userforissue__pari_issue__in=pari_issues)

    print("users : ", users, pari_issues)

    for _user in users:

        if user != _user:
            
            entry = f'''{user.username} a misé {user_for_issue.mise} ''' + DIPLODOCOIN_STR + f"sur le pari {pari.name}"
            JournalEntry.objects.create(entry_type = JournalEntryType.objects.get(entry_type = 'Pari'),
                                        user = _user,
                                        entry = entry)
    
    if pari.creator not in users:

        entry = f'''{user.username} a misé {user_for_issue.mise} ''' + DIPLODOCOIN_STR + f"sur le pari {pari.name}"
        JournalEntry.objects.create(entry_type = JournalEntryType.objects.get(entry_type = 'Pari'),
                                    user = pari.creator,
                                    entry = entry)




def write_journal_arena_get(user_in, user_out, coin_earned):

    for _user in User.objects.all():

        if _user == user_out:
            entry = f"{user_in.username} vous a expulsé de l'arène. Vous avez gagné {coin_earned} " + DIPLODOCOIN_STR

        elif _user == user_in:
            entry = f"Vous avez expulsé {user_out.username} de l'arène. Il a gagné {coin_earned} " + DIPLODOCOIN_STR
        
        else:
            entry = f"{user_in.username} a expulsé {user_out.username} de l'arène. {user_out.username} a gagné {coin_earned} " + DIPLODOCOIN_STR


        JournalEntry.objects.create(entry_type = JournalEntryType.objects.get(entry_type = 'Arène'),
                                    user = _user,
                                    entry = entry)


def write_journal_hdv_sold(seller, buyer, item, price):
        
        if item.type == 'box':
            item_str = 'box'
        else:
            item_str = Skin.objects.get(id=item.item_id).name

        entry = f"{buyer.username} vous a acheté {item_str} pour {price} " + DIPLODOCOIN_STR

        JournalEntry.objects.create(entry_type = JournalEntryType.objects.get(entry_type = 'HDV'),
                                    user = seller,
                                    entry = entry)


def write_journal_hdv_is_selling(seller, item, price):
        
        if item.type == 'box':
            item_str = 'box'
        else:
            item_str = Skin.objects.get(id=item.item_id).name

        entry = f"{seller.username} a mis en vente {item_str} pour {price} " + DIPLODOCOIN_STR

        for _user in User.objects.all():

            if _user != seller:
                JournalEntry.objects.create(entry_type = JournalEntryType.objects.get(entry_type = 'HDV'),
                                            user = _user,
                                            entry = entry)


def write_journal_tag(writer, receiver, session):

    if writer != receiver and receiver not in User.objects.filter(bot__isnull=False).distinct():

        entry = f"Vous avez été tagué par {writer.username.capitalize()} dans la session {session.session_name}"

        JournalEntry.objects.create(entry_type = JournalEntryType.objects.get(entry_type = 'Tag'),
                                    user = receiver,
                                    entry = entry)











