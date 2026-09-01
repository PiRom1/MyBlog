import base64
import datetime
from collections import Counter
from io import BytesIO

import numpy as np
from django.db.models import Count
from matplotlib.figure import Figure

from ..models import *


# Couleurs du thème (texte et axes en blanc sur fond transparent)
PLOT_FG = "w"
PLOT_LINE = "#ffc067"


def get_stats(session):
    """Retourne (users, yoda_stats, enjoy_stats) pour une session donnée.

    users : dict {username: nombre de messages}, trié par nombre décroissant.
    yoda_stats / enjoy_stats : listes alignées sur l'ordre de `users`.
    """
    rows = (
        Message.objects
        .filter(session_id=session)
        .values("writer__username", "writer__yoda_counter", "writer__enjoy_counter")
        .annotate(n_messages=Count("id"))
        .order_by("-n_messages")
    )

    users = {row["writer__username"]: row["n_messages"] for row in rows}
    yoda_stats = [row["writer__yoda_counter"] for row in rows]
    enjoy_stats = [row["writer__enjoy_counter"] for row in rows]

    return users, yoda_stats, enjoy_stats


def _formate_date(date):
    return f"{date.day:02d}/{date.month:02d}/{date.year}"


def _lisser(valeurs, fenetre):
    """Moyenne glissante. Renvoie une liste de len(valeurs) - fenetre + 1 éléments."""
    if fenetre <= 1:
        return list(valeurs)
    return [
        float(np.mean(valeurs[i:i + fenetre]))
        for i in range(len(valeurs) - fenetre + 1)
    ]


def get_messages_plot(messages, user, lissage=1):
    """Génère le graphe des messages par jour, encodé en base64 (PNG).

    Renvoie None s'il n'y a pas assez de données pour tracer quoi que ce soit.
    """
    messages = messages.order_by("pub_date")

    premier = messages.first()
    if premier is None:
        return None

    date0 = premier.pub_date.date()
    aujourdhui = datetime.datetime.now(datetime.timezone.utc).date()
    n_jours = (aujourdhui - date0).days + 1

    # Un seul passage sur les messages pour tout compter
    compte = Counter(message.pub_date.date() for message in messages)

    jours = [date0 + datetime.timedelta(days=x) for x in range(n_jours)]
    n_messages = [compte[jour] for jour in jours]

    # Lissage : on perd les (lissage - 1) premiers points
    lissage = max(1, min(lissage, len(jours)))
    n_messages = _lisser(n_messages, lissage)
    jours = jours[lissage - 1:]

    if not jours:
        return None

    dates = [_formate_date(jour) for jour in jours]

    # API objet : aucune figure globale, donc pas de conflit entre requêtes
    fig = Figure(figsize=(8, 4))
    ax = fig.subplots()

    ax.plot(dates, n_messages, color=PLOT_LINE)
    ax.set_title(
        f"Nombre de messages envoyés par jour par {user.username.capitalize()}",
        color=PLOT_FG,
    )
    ax.set_xlabel("Date", color=PLOT_FG)
    ax.set_ylabel("Nombre de messages", color=PLOT_FG)

    # Au maximum ~10 labels en abscisse, quelle que soit la durée couverte
    pas = max(1, len(dates) // 10)
    ax.set_xticks(dates[::pas])
    ax.tick_params(colors=PLOT_FG)
    for spine in ax.spines.values():
        spine.set_color(PLOT_FG)
    fig.autofmt_xdate(rotation=20)

    buffer = BytesIO()
    fig.savefig(buffer, format="png", transparent=True, bbox_inches="tight")

    return base64.b64encode(buffer.getvalue()).decode("utf-8")