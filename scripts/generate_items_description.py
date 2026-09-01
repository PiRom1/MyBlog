from Blog.models import Skin

def run():

    skins = {
        'Couleur de Texte':
            "Donnez à vos mots une couleur qui claque. Fini le random noir du prolo !",

        'Couleur de Fond':
            "Peignez le fond de vos messages à votre goût, aussi cataclysmique soit-il. Les autres n'auront qu'à s'y habituer !",

        'Couleur de Bordure':
            "Encadrez vos messages d'un liseré coloré du plus bel effet. Bon très vite vous ne l'utiliserez plus jamais, au profit d'une border image, mais eh. Hein ? Bon... ",

        "Couleur d'Avatar":
            "Cerclez votre avatar d'un anneau de couleur, comme un halo. Et calmez-vous, le comparatif entre Jésus et vous s'arrête là ... ",

        'Couleur de Nom':
            "Votre nom, mais en couleur. Parce que le noir c'est le mal ! Euuuh enfin je veux dire sur internet... Nooon mais en terme de beauté ! Arff non mais je veux dire... Oh et puis merde !",

        'Police':
            "NIQUE LA POLICE !! Euuh pardon, embellisez votre message d'une police d'écriture unique, tirée aléatoirement parmi un bon millier de polices ! Avec un peu de chances vous vous démarquerez comme jamais ! Mais dans la plupart des cas, personne ne verra la différence. Bon ...",

        'Emoji':
            "Un emoji que vous pouvez personnaliser sur mesure, à dégainer dans vos messages ! Bon on se croirait un peu sur JVC, mais ici au moins on est CERTAIN, et sans rigoler, de pouvoir combattre un gorille à main nu. Triompher ? C'est autre chose ... ",

        "Image d'arrière plan":
            "Tapissez votre écran d'une image de fond somptueuse, car comme on vous l'a sans doute rabâché depuis votre enfance : `Tu feras ce que tu voudras quand tu seras chez toi !`. Eh bien votre compte Diplo, c'est chez vous !",

        'Ornement de message':
            "Habillez vos messages d'un cadre sacrément inspiré, et ainsi vous détournerez l'attention du texte catastrophique que vous êtes en train d'écrire ! Eh oui, nous avons pensé à tout !",

        'Nom RGB':
            "Votre nom scintille de mille couleurs, en boucle, pour l'éternité (non négociable, non échangeable ni remboursable)",

        'Ornement RGB':
            "Si vous ne brillerez jamais par votre intelligence, permettez au moins à vos messages piteux de rayonner d'un halo lumineux, coloré et dynamique ! Envahissant, tapageur, et relativement inutile. Non je ne vous décris pas, je parle toujours de l'item !",

        'Médaille de la condamnation pour fraude DiploFiscale':
            "Une médaille réservée aux multirécidivistes de l'article 148-B du DiplodoCode Civil, décernée non sans un soupir largement mérité de la part de l'assemblée du tribunal DiploJudiciaire. Elle ne sert à rien, n'a aucune valeur, et s'accorde donc parfaitement avec son détenteur."
    }

    for skin_name, description in skins.items():
        updated = Skin.objects.filter(name=skin_name).update(description=description)
        if updated == 0:
            print(f"⚠️  Aucun skin nommé '{skin_name}' trouvé")
        else:
            print(f"✓ {skin_name}")