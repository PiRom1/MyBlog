from Blog.models import User, Session, Message
from datetime import datetime

def run():

    session = Session.objects.get(session_name='Chat Acelys')
    user = User.objects.get(username='juge')
    text = f'''
            Bonjour à tous. <br>
                Par ce message je viens tester la fonctionnalité des tâches. Ainsi je pourrai lancer l'analyse du chat automatisée tous les jours à la même heure. <br>
            J'en profite pour vous souhaiter à tous une excellente journée !<br>
            Jugement vôtre, <br><br>
            Le Juge, {datetime.now().day}/{datetime.now().month}/{datetime.now().year}, {datetime.now().hour}h{datetime.now().minute}
            '''
    Message.objects.create(writer = user,
                           session_id = session,
                           text = text)