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

from .utils.stats import *
import random
import bleach

VERBS = ['accepter', 'acheter', 'affaiblir', 'agir', 'aimer', 'aller', 'appartenir', 'appeler', 'apprendre', 'arriver', 'attaquer', 'attendre', 'avoir', 'baisser', 'blanchir', 'boire', 'briser', 'bâtir', 'causer', 'chanter', 'chercher', 'choisir', 'commencer', 'comprendre', 'confondre', 'connaître', 'contenir', 'contredire', 'contrevenir', 'convenir', 'correspondre', 'couper', 'croire', 'danser', 'demander', 'descendre', 'devenir', 'deviner', 'devoir', 'dire', 'donner', 'défendre', 'démolir', 'dépendre', 'désobéir', 'détenir', 'entendre', 'entrer', 'explorer', 'faire', 'falloir', 'fermer', 'finir', 'fondre', 'fournir', 'fumer', 'gagner', 'garder', 'gaspiller', 'grandir', 'habiller', 'habiter', 'hésiter', 'ignorer', 'indiquer', 'interdire', 'inviter', 'jaunir', 'jouer', 'jurer', 'justifier', 'klaxonner', 'laisser', 'laver', 'lire', 'louer', 'maigrir', 'manger', 'marcher', 'mesurer', 'mettre', 'monter', 'montrer', 'mourir', 'médire', 'naître', 'nier', 'noter', 'nourrir', 'obéir', 'oublier', 'paraître', 'parler', 'partir', 'passer', 'payer', 'pendre', 'penser', 'perdre', 'pouvoir', 'prendre', 'prédire', 'qualifier', 'quitter', 'raconter', 'ralentir', 'redire', 'regarder', 'remplir', 'rendre', 'rentrer', 'rester', 'retenir', 'retourner', 'revenir', 'rougir', 'réfléchir', 'répondre', 'réunir', 'réussir', 'saisir', 'salir', 'sauter', 'savoir', 'sentir', 'signer', 'sortir', 'subir', 'tendre', 'tenir', 'tenter', 'tomber', 'tondre', 'tordre', 'travailler', 'traverser', 'trouver', 'unir', 'user', 'utiliser', 'vendre', 'venir', 'vieillir', 'vivre', 'voir', 'voler', 'vouloir', 'vérifier', 'écouter', 'écrire', 'étendre', 'être']
VERBS_PRE = ["j'accepte", "j'achète", "j'affaiblis", "j'agis", "j'aime", "je vais", "j'appartiens", "j'appelle", "j'apprends", "j'arrive", "j'attaque", "j'attends", "j'ai", "je baisse", "je blanchis", "je bois", "je brise", "je bâtis", "je cause", "je chante", "je cherche", "je choisis", "je commence", "je comprends", "je confonds", "je connais", "je contiens", "je contredis", "je contreviens", "je conviens", "je corresponds", "je coupe", "je crois", "je danse", "je demande", "je descends", "je deviens", "je devine", "je dois", "je dis", "je donne", "je défends", "je démolis", "je dépends", "je désobéis", "je détiens", "j'entends", "j'entre", "j'explore", "je fais", "il faut", "je ferme", "je finis", "je fonds", "je fournis", "je fume", "je gagne", "je garde", "je gaspille", "je grandis", "je m'habille", "j'habite", "j'hésite", "j'ignore", "j'indique", "j'interdis", "j'invite", "je jaunis", "je joue", "je jure", "je justifie", "je klaxonne", "je laisse", "je lave", "je lis", "je loue", "je maigris", "je mange", "je marche", "je mesure", "je mets", "je monte", "je montre", "je meurs", "je médit", "je nais", "je nie", "je note", "je nourris", "j'obéis", "j'oublie", "je parais", "je parle", "je pars", "je passe", "je paie", "je pends", "je pense", "je perds", "je peux", "je prends", "je prédis", "je qualifie", "je quitte", "je raconte", "je ralentis", "je redis", "je regarde", "je remplis", "je rends", "je rentre", "je reste", "je retiens", "je retourne", "je reviens", "je rougis", "je réfléchis", "je réponds", "je réunis", "je réussis", "je saisis", "je salis", "je saute", "je sais", "je sens", "je signe", "je sors", "je subis", "je tends", "je tiens", "je tente", "je tombe", "je tonds", "je tords", "je travaille", "je traverse", "je trouve", "j'unis", "j'use", "j'utilise", "je vends", "je viens", "je vieillis", "je vis", "je vois", "je vole", "je veux", "je vérifie", "j'écoute", "j'écris", "j'étends", "je suis"]
VERBS_PP = ["accepté", "acheté", "affaibli", "agi", "aimé", "allé", "appartenu", "appelé", "appris", "arrivé", "attaqué", "attendu", "eu",  "baissé", "blanchi", "bu", "brisé", "bâti", "causé", "chanté", "cherché", "choisi", "commencé", "compris", "confondu",  "connu", "contenu", "contredit", "contrevenu", "convenu", "correspondu", "coupé", "cru", "dansé", "demandé", "descendu",  "devenu", "deviné", "dû", "dit", "donné", "défendu", "démoli", "dépendu", "désobéi", "détenu", "entendu", "entré",  "exploré", "fait", "fallu", "fermé", "fini", "fondu", "fourni", "fumé", "gagné", "gardé", "gaspillé", "grandi", "habillé",  "habité", "hésité", "ignoré", "indiqué", "interdit", "invité", "jauni", "joué", "juré", "justifié", "klaxonné", "laissé", "lavé",  "lu", "loué", "maigri", "mangé", "marché", "mesuré", "mis", "monté", "montré", "mort", "médît", "né", "nié", "noté",  "nourri", "obéi", "oublié", "paru", "parlé", "parti", "passé", "payé", "pendu", "pensé", "perdu", "pu", "pris", "prédit",  "qualifié", "quitté", "raconté", "ralenti", "re-dit", "regardé", "rempli", "rendu", "rentré", "resté", "retenu", "retourné",  "revenu", "rougi", "réfléchi", "répondu", "réuni", "réussi", "saisi", "sali", "sauté", "su", "senti", "signé", "sorti",  "subi", "tendu", "tenu", "tenté", "tombé", "tondu", "tordu", "travaillé", "traversé", "trouvé", "uni", "usé", "utilisé", "vendu",  "venu", "vieilli", "vécu", "vu", "volé", "voulu", "vérifié", "écouté", "écrit", "étendu", "été"]
VERBS_PS = ["j'acceptai", "j'achetai", "j'affaiblis", "j'agis", "j'aimai", "j'allai", "j'appartins", "j'appelai", "j'appris", "j'arrivai", "j'attaquai", "j'attendis", "j'eus",  "je baissai", "je blanchis", "je bus", "je brisai", "je bâtis", "je causai", "je chantai", "je cherchai", "je choisis", "je commençai", "je compris", "je confondis",  "je connus", "je contins", "je contredis", "je contrevins", "je convins", "je correspondis", "je coupai", "je crus", "je dansai", "je demandai", "je descendis",  "je devins", "je devinai", "je dus", "je dis", "je donnai", "je défendis", "je démolis", "je dépendis", "je désobéis", "je détins", "j'entendis", "j'entrai",  "j'explorai", "je fis", "il fallut", "je fermai", "je finis", "je fondis", "je fournis", "je fumai", "je gagnai", "je gardai", "je gaspillai", "je grandis", "je m'habillai",  "j'habitai", "j'hésitai", "j'ignorai", "j'indiquai", "j'interdis", "j'invitai", "je jaunis", "je jouai", "je jurai", "je justifiai", "je klaxonnai", "je laissai", "je lavai",  "je lus", "je louai", "je maigris", "je mangeai", "je marchai", "je mesurai", "je mis", "je montai", "je montrai", "je mourus", "je médit", "je naquis", "je niai", "je notai",  "je nourris", "j'obéis", "j'oubliai", "je parus", "je parlai", "je partis", "je passai", "je payai", "je pendis", "je pensai", "je perdis", "je pus", "je pris", "je prédis",  "je qualifiai", "je quittai", "je racontai", "je ralentis", "je redis", "je regardai", "je remplis", "je rendis", "je rentrai", "je restai", "je retins", "je retournai",  "je revins", "je rougis", "je réfléchis", "je répondis", "je réunis", "je réussis", "je saisis", "je salis", "je sautai", "je sus", "je sentis", "je signai", "je sortis",  "je subis", "je tendis", "je tins", "je tentai", "je tombai", "je tondis", "je tordis", "je travaillai", "je traversai", "je trouvai", "j'unis", "j'usai", "j'utilisai", "je vendis",  "je vins", "je vieillis", "je vécus", "je vis", "je volai", "je voulus", "je vérifiai", "j'écoutai", "j'écrivis", "j'étendis", "je fus"]
VERBS_IMP = ["j'acceptais", "j'achetais", "j'affaiblissais", "j'agissais", "j'aimais", "j'allais", "j'appartenais", "j'appelais", "j'apprenais", "j'arrivais", "j'attaquais", "j'attendais", "j'avais",  "je baissais", "je blanchissais", "je buvais", "je brisais", "je bâtissais", "je causais", "je chantais", "je cherchais", "je choisissais", "je commençais", "je comprenais", "je confondais",  "je connaissais", "je contenais", "je contredisais", "je contrevenais", "je convenais", "je correspondais", "je coupais", "je croyais", "je dansais", "je demandais", "je descendais",  "je devenais", "je devinais", "je devais", "je disais", "je donnais", "je défendais", "je démolissais", "je dépendais", "je désobéissais", "je détenais", "j'entendais", "j'entrais",  "j'explorais", "je faisais", "il fallait", "je fermais", "je finissais", "je fondais", "je fournissais", "je fumais", "je gagnais", "je gardais", "je gaspillais", "je grandissais", "je m'habillais",  "j'habitais", "j'hésitais", "j'ignorais", "j'indiquais", "j'interdisais", "j'invitais", "je jaunissais", "je jouais", "je jurais", "je justifiais", "je klaxonnais", "je laissais", "je lavais",  "je lisais", "je louais", "je maigrissais", "je mangeais", "je marchais", "je mesurais", "je mettais", "je montais", "je montrais", "je mourais", "je médisais", "je naissais", "je niais", "je notais",  "je nourrissais", "j'obéissais", "j'oubliais", "je paraissais", "je parlais", "je partais", "je passais", "je payais", "je pendais", "je pensais", "je perdais", "je pouvais", "je prenais", "je prédisais",  "je qualifiais", "je quittais", "je racontais", "je ralentissais", "je redisais", "je regardais", "je remplissais", "je rendais", "je rentrais", "je restais", "je retenais", "je retournais",  "je revenais", "je rougissais", "je réfléchissais", "je répondais", "je réunissais", "je réussissais", "je saisissais", "je salissais", "je sautais", "je savais", "je sentais", "je signais", "je sortais",  "je subissais", "je tendais", "je tenais", "je tentais", "je tombais", "je tondais", "je tordais", "je travaillais", "je traversais", "je trouvais", "j'unissais", "j'usais", "j'utilisais", "je vendais",  "je venais", "je vieillissais", "je vivais", "je voyais", "je volais", "je voulais", "je vérifiais", "j'écoutais", "j'écrivais", "j'étendais", "j'étais"]
VERBS_F = ["j'accepterai", "j'achèterai", "j'affaiblirai", "j'agirai", "j'aimerai", "j'irai", "j'appartiendrai", "j'appellerai", "j'apprendrai", "j'arriverai", "j'attaquerai", "j'attendrai", "j'aurai",  "je baisserai", "je blanchirai", "je boirai", "je briserai", "je bâtirai", "je causerai", "je chanterai", "je chercherai", "je choisirai", "je commencerai", "je comprendrai", "je confondrai",  "je connaîtrai", "je contiendrai", "je contredirai", "je contreviendrai", "je conviendrai", "je correspondrai", "je couperai", "je croirai", "je danserai", "je demanderai", "je descendrai",  "je deviendrai", "je devinerai", "je devrai", "je dirai", "je donnerai", "je défendrai", "je démolirai", "je dépendrai", "je désobéirai", "je détiendrai", "j'entendrai", "j'entrerai",  "j'explorerai", "je ferai", "il faudra", "je fermerai", "je finirai", "je fondrai", "je fournirai", "je fumerai", "je gagnerai", "je garderai", "je gaspillerai", "je grandirai", "je m'habillerai",  "j'habiterai", "j'hésiterai", "j'ignorerai", "j'indiquerai", "j'interdirai", "j'inviterai", "je jaunirai", "je jouerai", "je jurerai", "je justifierai", "je klaxonnerai", "je laisserai", "je laverai",  "je lirai", "je louerai", "je maigrirai", "je mangerai", "je marcherai", "je mesurerai", "je mettrai", "je monterai", "je montrerai", "je mourrai", "je médirai", "je naîtrai", "je nierai", "je noterai",  "je nourrirai", "j'obéirai", "j'oublierai", "je paraîtrai", "je parlerai", "je partirai", "je passerai", "je paierai", "je pendrai", "je penserai", "je perdrai", "je pourrai", "je prendrai", "je prédirai",  "je qualifierai", "je quitterai", "je raconterai", "je ralentirai", "je redirai", "je regarderai", "je remplirai", "je rendrai", "je rentrerai", "je resterai", "je retiendrai", "je retournerai",  "je reviendrai", "je rougirai", "je réfléchirai", "je répondrai", "je réunirai", "je réussirai", "je saisirai", "je salirai", "je sauterai", "je saurai", "je sentirai", "je signerai", "je sortirai",  "je subirai", "je tendrai", "je tiendrai", "je tenterai", "je tomberai", "je tondrai", "je tordrai", "je travaillerai", "je traverserai", "je trouverai", "j'unirai", "j'userai", "j'utiliserai", "je vendrai",  "je viendrai", "je vieillirai", "je vivrai", "je verrai", "je volerai", "je voudrai", "je vérifierai", "j'écouterai", "j'écrirai", "j'étendrai", "je serai"]
VERBS_COND = ["j'accepterais", "j'achèterais", "j'affaiblirais", "j'agirais", "j'aimerais", "j'irais", "j'appartiendrais", "j'appellerais", "j'apprendrais", "j'arriverais", "j'attaquerais", "j'attendrais", "j'aurais",  "je baisserais", "je blanchirais", "je boirais", "je briserais", "je bâtirais", "je causerais", "je chanterais", "je chercherais", "je choisirais", "je commencerais", "je comprendrais", "je confondrais",  "je connaîtrais", "je contiendrais", "je contredirais", "je contreviendrais", "je conviendrais", "je correspondrais", "je couperais", "je croirais", "je danserais", "je demanderais", "je descendrais",  "je deviendrais", "je devinerais", "je devrais", "je dirais", "je donnerais", "je défendrais", "je démolirais", "je dépendrais", "je désobéirais", "je détiendrais", "j'entendrais", "j'entrerais",  "j'explorerais", "je ferais", "il faudrait", "je fermerais", "je finirais", "je fondrais", "je fournirais", "je fumerais", "je gagnerais", "je garderais", "je gaspillerais", "je grandirais", "je m'habillerais",  "j'habiterais", "j'hésiterais", "j'ignorerais", "j'indiquerais", "j'interdirais", "j'inviterais", "je jaunirais", "je jouerais", "je jurerais", "je justifierais", "je klaxonnerais", "je laisserais", "je laverais",  "je lirais", "je louerais", "je maigrirais", "je mangerais", "je marcherais", "je mesurerais", "je mettrais", "je monterais", "je montrerais", "je mourrais", "je médirais", "je naîtrais", "je nierais", "je noterais",  "je nourrirais", "j'obéirais", "j'oublierais", "je paraîtrais", "je parlerais", "je partirais", "je passerais", "je paierais", "je pendrais", "je penserais", "je perdrais", "je pourrais", "je prendrais", "je prédirais",  "je qualifierais", "je quitterais", "je raconterais", "je ralentirais", "je redirais", "je regarderais", "je remplirais", "je rendrais", "je rentrerais", "je resterais", "je retiendrais", "je retournerais",  "je reviendrais", "je rougirais", "je réfléchirais", "je répondrais", "je réunirais", "je réussirais", "je saisirais", "je salirais", "je sauterais", "je saurais", "je sentirais", "je signerais", "je sortirais",  "je subirais", "je tendrais", "je tiendrais", "je tenterais", "je tomberais", "je tondrais", "je tordrais", "je travaillerais", "je traverserais", "je trouverais", "j'unirais", "j'userais", "j'utiliserais", "je vendrais",  "je viendrais", "je vieillirais", "je vivrais", "je verrais", "je volerais", "je voudrais", "je vérifierais", "j'écouterais", "j'écrirais", "j'étendrais", "je serais"]


ENJOY_PATTERNS = ["quelle heure est il enjoy",
                  "quelle heure il est enjoy",
                  "enjoy il est quelle heure",
                  "enjoy quelle heure est il"]


CALEMBOURS_PATTERNS = [(' quoi ', ' quoi(feur) '),
                       (' oui ', ' oui(stiti) '),
                       (' qui ', ' qui(quette) ' ),
                       (' ou ', ' ou(lligan) '),
                       (' mais ', ' mais(on) '),
                       (' pour ', ' pour(boire) '),
                       (' romain ', ' romain(tello) '),
                       ]

SENTENCE_CALEMBOUR = "<br><br>Vous avez été corrompu par le <strong>bot-ade</strong>, roi de la boutade !"



def theophile(text):
    # Infinitif
    pattern = r'\b(?:' + '|'.join(map(re.escape, VERBS)) + r')\b'
    text = re.sub(pattern, 'picoler', text, flags=re.IGNORECASE)
    # Présent
    pattern = r'\b(?:' + '|'.join(map(re.escape, VERBS_PRE)) + r')\b'
    text = re.sub(pattern, 'je picole', text, flags=re.IGNORECASE)
    # Participe passé
    pattern = r'\b(?:' + '|'.join(map(re.escape, VERBS_PP)) + r')\b'
    text = re.sub(pattern, 'picolé', text, flags=re.IGNORECASE)
    # Passé simple
    pattern = r'\b(?:' + '|'.join(map(re.escape, VERBS_PS)) + r')\b'
    text = re.sub(pattern, 'je picolai', text, flags=re.IGNORECASE)
    # Imparfait
    pattern = r'\b(?:' + '|'.join(map(re.escape, VERBS_IMP)) + r')\b'
    text = re.sub(pattern, 'je picolais', text, flags=re.IGNORECASE)
    # Futur
    pattern = r'\b(?:' + '|'.join(map(re.escape, VERBS_F)) + r')\b'
    text = re.sub(pattern, 'je picolerai', text, flags=re.IGNORECASE)
    # Conditionnel
    pattern = r'\b(?:' + '|'.join(map(re.escape, VERBS_COND)) + r')\b'
    text = re.sub(pattern, 'je picolerais', text, flags=re.IGNORECASE)
    return text

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
        
        messages_html = render_to_string('Blog\chat\messages.html', {
            'messages': messages,
            'user': user,
            'years': years,
            'month': month,
            'day': day,
            'when_new_date': when_new_date,
            'new_message': new_message})
        
        return JsonResponse({'messages_html': messages_html,
                             'last_message_id': last_message_id})

    if request.method == "POST":
        message_form = MessageForm(request.POST)

        if message_form.is_valid():
            new_message = message_form['message']
            color = message_form['color'].value()
            #user = message_form['who']
            text = new_message.value()

            
            for enjoy_pattern in ENJOY_PATTERNS:
                if enjoy_pattern in text.lower().replace('-',' '):
                    new_message = Message(writer = user, text = "[A demandé l'heure à Enjoy]", pub_date = timezone.now(), color = color, session_id = session)
                    new_message.save()
                    return HttpResponseRedirect('http://www.quelleheureestilenjoy.com/')


            #user = user.get_username()
            #user = User.objects.filter(name = user)[0]
            print(text)
            code = (text.split(':')[0]).lower().strip()
            if code == "nouveauticket":
                # Redirection vers la page de création de ticket avec le message pré-rempli
                new_message = Message(writer = user, text = text, pub_date = timezone.now(), color = color, session_id = session)
                new_message.save()
                return redirect('create_ticket')
            
            if code == "sondage":
                # Redirection vers la page de création de sondage avec le message pré-rempli
                new_message = Message(writer = user, text = text, pub_date = timezone.now(), color = color, session_id = session)
                new_message.save()
                return redirect('create_sondage')
            
            # theophile
            if random.random() < 0.10:
                text = re.sub(r'théophile|theophile|théo|theo', "l'alcoolo de service", text, flags=re.IGNORECASE)
            if user.username == "theophile" and len(text) < 200 and random.random() < 0.05:
                text = theophile(text)

            # url parsing
            text = bleach.linkify(text)
            text = bleach.clean(text, tags=settings.ALLOWED_TAGS, attributes=settings.ALLOWED_ATTRIBUTES)
                
            # youtube parsing
            ytb_addon = ''
            for i in range(text.count("\"https://www.youtube.com/watch")):
                code = text.split('\"https://www.youtube.com/watch?v=')[i+1]
                code = code.split("\"")[0]

                ytb_addon += f"<br><br><iframe width='420' height='345' src='https://www.youtube.com/embed/{code}'></iframe>"
            text += ytb_addon

            # Calembours
            if random.random() < 0.1:
                calembour = False
                for pattern in CALEMBOURS_PATTERNS:    
                    index = text.lower().find(pattern[0])
                    while index != -1:
                        text = text.replace(text[index:index+len(pattern[0])], pattern[1])
                        calembour = True
                        index = text.lower().find(pattern[0])
                if calembour:
                    text += SENTENCE_CALEMBOUR

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

    
    message_stats, yoda_stats = get_stats(session)

    print(message_stats)
    print(yoda_stats)

    url = "Blog/chat/stats.html"
    context = {"message_stats" : message_stats,
               "yoda_stats" : yoda_stats,
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

    url = "Blog/user/user.html"
    context = {'viewed_user' : viewed_user,
               'n_messages' : n_messages,
               'form' : form,
               'messages' : messages,
               'words' : words
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


def increment_view(request):
    if request.method == 'POST':
        user = request.user  # Récupérer l'objet
        user.yoda_counter += 1  # Incrémenter le compteur
        user.save()  # Sauvegarder en base
        return JsonResponse({'status': 'ok', 'new_value': user.yoda_counter})
    

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

