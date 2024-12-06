## Script that turns every sondages which session is none to sondages to Chat Acelys session.
## (Because historically, sondages were shared across sessions)

from Blog.models import Sondage, Session

def run():
    default_session = Session.objects.get(session_name='Chat Acelys')
    sondages = Sondage.objects.filter(session=None)
    sondages.update(session=default_session)
    return {"success" : True}

if __name__ == '__main__':
    run()
