from ..models import *
import numpy as np
import datetime
import matplotlib.pyplot as plt
from io import BytesIO
import base64


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



def get_messages_plot(messages, user):

    def formate_date(date):
        

        return f"{date.day}/{date.month}/{date.year}"

    dates = [message.pub_date.date() for message in messages]
    uniq_dates = sorted(list(set(dates)))
    
    dates = np.array([formate_date(date) for date in dates])
    uniq_dates = np.array([formate_date(date) for date in uniq_dates])
    
    n_messages = [np.sum(dates == date) for date in uniq_dates]

    params = {"ytick.color" : "w",
            "xtick.color" : "w",
            "axes.labelcolor" : "w",
            "axes.edgecolor" : "w",
            "text.color" : "w"}
    plt.rcParams.update(params)

    plot = plt.plot(uniq_dates, n_messages, color='#ffc067')
    plt.title(f"Nombre de messages envoyés par jour par {user.username.capitalize()}")
    plt.xticks(uniq_dates[::10], rotation=20)
    plt.xlabel("Date")
    plt.ylabel("Nombre de messages")

    buffer = BytesIO()
    plt.savefig(buffer, format='png', transparent=True)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    plt.close()
    return graphic
    
