from ..models import *
import numpy as np

def get_stats(session):

    messages = Message.objects.filter(session_id = session)
    users = {}

    for message in messages:
        username = message.writer.username
        if username not in users:
            users[username] = 1
        else:
            users[username] += 1
    

    
    a = list(users.items())
    keys = [i[0] for i in a]
    values = [i[1] for i in a]

    ranks = np.argsort(values)[-1::-1]

    users = {}

    for i in ranks:
        users[keys[i]] = values[i]


    print(users)

    yoda_stats = [User.objects.get(username=user).yoda_counter for user in users.keys()]
    print(yoda_stats)

    return users, yoda_stats
