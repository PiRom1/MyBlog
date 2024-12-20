from Blog.models import EnjoyTimestamp, User
from datetime import datetime, timedelta
import random as rd



def run():
    for i in range(500):
        user = User.objects.get(username='romain')
        EnjoyTimestamp.objects.create(time=datetime.now() + timedelta(hours=rd.randint(0, 23)) + timedelta(minutes=rd.randint(0, 59)),
                                    published_date=datetime.now(),
                                    writer=user,
                                    comment='celui là est génial !')


if __name__ == 'main':
    run()
        




