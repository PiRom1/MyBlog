from ..models import Message
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.shortcuts import render, redirect
import random as rd
import re
import bleach
from django.conf import settings
from markdown import Markdown

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
                       (' mais ', ' mais(téo) '),
                       (' pour ', ' pour(boire) '),
                       (' romain ', ' romain(tello) '),
                       (' louis' , ' (actua)louis '),
                       (' léon ', ' (accord)léon '),
                       (' melvin ',' melvin(asse) '),
                       (' antony ',' antony(ktmaère) '),
                       (' rachid ',' (a)rachid '),
                       (' donc ',' (pé)donc(ule) '),
                       (' philippe ', ' (jen)philippe(er vite monslip) '),
                       (' salwa ', ' salwa(naconda) ' ),
                       ('lise')
                       (' très ', ' très(te négrière) '),
                       (' champignon ', ' cham(bragaz)pignon '),
                       (' tant ', ' tant(dinite) '),
                       (' ordi ', ' ordi(nosaure) '),
                       (' acelys ', ' acelys(térique) '),
                       (' lexpilot ', " lex(baisse ta culotte c'est moi qui)pilot "),
                       (' pause ', ' pause (de 3 heures) '),
                       (' code ',' cod(éine) '),
                       (' champ ', ' cham(bragaz) '),
                       (' avance ', ' avanc(éphalopode) '),
                       (' argent ', ' argent(marie le pen) '),
                       (' police ', ' police(rael) '),
                       (' repas ', ' repas(lestine) '),
                       ('ping', "(putain fait chier j'ai 300 de)ping"),
                       (' botade ', '  '),
                       (' conges ', ' conges(nocide armenien) '),
                       (' congès ', ' congès(nocide armenien) '),
                       (' congés ', ' congés(nocide armenien) '),
                       (' facultatif ', ' facultatif(fany(ktamere)) '),
                       (' dino ', ' dino(rdahl Lelandais) '),

                       ]

SENTENCE_CALEMBOUR = "<br><br>Vous avez été corrompu par le <strong>bot-ade</strong>, roi de la boutade !"

md = Markdown(extensions=['markdown.extensions.fenced_code', 'markdown.extensions.codehilite', 'markdown.extensions.tables', 'markdown.extensions.sane_lists', 'markdown.extensions.nl2br', 'markdown.extensions.smarty'])


def enjoy(text, user, session):
    for enjoy_pattern in ENJOY_PATTERNS:
                    print(1)
                    if enjoy_pattern in text.lower().replace('-',' '):
                        print('ouiii')
                        new_message = Message(writer = user, text = "[A demandé l'heure à Enjoy]", pub_date = timezone.now(), session_id = session)
                        new_message.save()
                        user.enjoy_counter += 1
                        user.save()
                        return HttpResponseRedirect('http://www.quelleheureestilenjoy.com/')


def ticket_sondage(text, user, session):
            code = (text.split(':')[0]).lower().strip()
            if code == "nouveauticket":
                # Redirection vers la page de création de ticket avec le message pré-rempli
                new_message = Message(writer = user, text = text, pub_date = timezone.now(), session_id = session)
                new_message.save()
                return redirect('create_ticket')
            
            if code == "sondage":
                # Redirection vers la page de création de sondage avec le message pré-rempli
                new_message = Message(writer = user, text = text, pub_date = timezone.now(), session_id = session)
                new_message.save()
                return redirect('create_sondage')

def process_theophile(text, user):
    # theophile

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



    if rd.random() < 0.10:
        text = re.sub(r'théophile|theophile|théo|theo', "l'alcoolo de service", text, flags=re.IGNORECASE)
    if user.username == "theophile" and len(text) < 200 and rd.random() < 0.05:
        text = theophile(text)

    return text


def url_parsing(text):
    
    # url parsing
    text = bleach.linkify(text)
    text = bleach.clean(text, tags=settings.ALLOWED_TAGS, attributes=settings.ALLOWED_ATTRIBUTES)

    return text


def youtube_parsing(text):
    
    # # youtube parsing
    # ytb_addon = ''
    # for i in range(text.count("\"https://www.youtube.com/watch")):
    #     code = text.split('\"https://www.youtube.com/watch?v=')[i+1]
    #     code = code.split("\"")[0]

    #     ytb_addon += f"<br><br><iframe width='420' height='345' src='https://www.youtube.com/embed/{code}'></iframe>"
    # text += ytb_addon
    text = text.replace('oembed url', 'iframe src')
    text = text.replace('/oembed', '/iframe')
    text = text.replace('youtube.com/watch?v=', 'youtube.com/embed/')

    return text


def calembours(text):

    # Calembours
    if rd.random() < 0.1:
        calembour = False
        for pattern in CALEMBOURS_PATTERNS:    
            index = text.lower().find(pattern[0])
            while index != -1:
                text = text.replace(text[index:index+len(pattern[0])], pattern[1])
                calembour = True
                index = text.lower().find(pattern[0])
        if calembour:
            text += SENTENCE_CALEMBOUR
    
    return text


def reglys(text):
            
    # Reglys
    text = text.replace('reglys', '<del>reglys</del> ConformIA')
    text = text.replace('Reglys', '<del>Reglys</del> ConformIA')

    return text

def replace_words(text):
    rand = rd.random()
    if text in ['lise', 'Lise']:
        if rand < 0.5:
            text = '<del>Lise</del> Louise'
        else:
            text = 'Louise'
    elif text in ['louise', 'Louise']:
        text = 'Lise'
    return text


def process_text(text, user, session):
    
    res = enjoy(text, user, session)
    if not res:
        res = ticket_sondage(text, user, session)
    print("Res : ", res)
    if res:
         print("res", res)
         return res

    
    # text = md.convert(text)
    print("text1 : ", text)
    text = process_theophile(text, user)
    # text = url_parsing(text)
    print("text2 : ", text)
    text = youtube_parsing(text)
    text = calembours(text)
    text = reglys(text)
    text = replace_words(text)
    

    return text