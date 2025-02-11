import json
from Blog.models import User, Game, GameScore
import os

def run():

    print(os.listdir())

    path = 'scripts/game_scores.json'


    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)  # Charge le contenu JSON en dict


    for k,v in data.items():
        # print("key : ", k, "value : ", v)
        game = v.get('game')
        score = v.get('score')
        user_id = v.get('user_id')
        date = v.get('date')

        if score != 9999:
            
            GameScore.objects.create(game = Game.objects.get(name=game.lower()),
                                    score = score,
                                    user = User.objects.get(id=user_id),
                                    date = date)
        