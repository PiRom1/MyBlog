import sqlite3
import json
import os

def run():
    # Modify the database path as necessary
    db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'my_blog.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Fetch all entries from game_score table
    cur.execute("SELECT * FROM GameScore")
    rows = cur.fetchall()
    # Get column names
    columns = [desc[0] for desc in cur.description]
    
    # Build a list of dicts for each row
    data = [dict(zip(columns, row)) for row in rows]
    
    # Save data to JSON file
    output_file = os.path.join(os.path.dirname(__file__), 'game_scores.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Scores have been saved to {output_file}")
    
if __name__ == "__main__":
    run()
