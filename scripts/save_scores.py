import sqlite3
import json
import os
from Blog.models import GameScore

def run():
    # Get scores from database
    scores = GameScore.objects.all()
    data = {}
    for score in scores:
        data[score.id] = {
            'game': score.game,
            'score': score.score,
            'user_id': score.user.id,
            'date': score.date
        }
 
    # Save data to JSON file
    output_file = os.path.join(os.path.dirname(__file__), 'game_scores.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Scores have been saved to {output_file}")
    
if __name__ == "__main__":
    run()
