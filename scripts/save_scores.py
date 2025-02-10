import sqlite3
import json
import os
from Blog.models import GameScore

def run():
    # Get scores from database
    scores = GameScore.objects.all()
    data = {}
    for score in scores:
        for attribute in score.__dict__:
            if attribute not in ['_state', 'id']:
                if attribute not in data:
                    data[attribute] = []
                data[attribute].append(getattr(score, attribute))

    
    # Save data to JSON file
    output_file = os.path.join(os.path.dirname(__file__), 'game_scores.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Scores have been saved to {output_file}")
    
if __name__ == "__main__":
    run()
