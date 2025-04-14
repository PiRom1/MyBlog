from tqdm import tqdm
import json
from Blog.utils.dw_battle_logic import *
from Blog.models import DWUserDino, DWUserTeam, User
from Blog.views.dinowars_views import calculate_total_stats
import pandas as pd

def run():
    user = User.objects.get(username='louis')
    fight_stats = {}
    for dino in DWUserDino.objects.filter(user=user):
        fight_stats[dino.dino.name] = {
            'dmg': 0,
            'hp_lost': 0,
            'hp_left': 0,
            'hp_left_count': 0,  # Count of battles where dino survived
            'deaths': 0,         # Count of battles where dino died
            'wins': 0,
            'losses': 0,
            'battles': 0,        # Total battles participated in
            'attacks': 0,        # Number of attacks performed
            'death_ticks': [],   # List to store tick numbers when dino died
            'battle_durations': [],  # List to store battle durations when dino died
            'lost_when_dead': 0, # Number of battles lost when this dino died
            'interval_stats': {
                '0-200': {'deaths': 0, 'losses': 0, 'weight': 0.04},
                '200-300': {'deaths': 0, 'losses': 0, 'weight': 0.06},
                '300-400': {'deaths': 0, 'losses': 0, 'weight': 0.13},
                '400-500': {'deaths': 0, 'losses': 0, 'weight': 0.19},
                '500-600': {'deaths': 0, 'losses': 0, 'weight': 0.26},
                '600-+': {'deaths': 0, 'losses': 0, 'weight': 0.32},
            },
            'impact_score': 0,  # Placeholder for impact score
        }
    
    possible_teams = []
    already_checked = []
    # Define the tick intervals
    intervals = [
        (0, 200),
        (200, 300),
        (300, 400),
        (400, 500),
        (500, 600),
        (600, float('inf'))
    ]
    
    for dino1 in DWUserDino.objects.filter(user=user):
        already_checked.append(dino1.id)
        already_checked_2 = already_checked.copy()
        for dino2 in DWUserDino.objects.filter(user=user).exclude(id__in=already_checked):
            already_checked_2.append(dino2.id)
            for dino3 in DWUserDino.objects.filter(user=user).exclude(id__in=already_checked_2):
                possible_teams.append([dino1, dino2, dino3])
    
    assert len(possible_teams) == 84, f"Expected 84 teams, got {len(possible_teams)}"
    
    team_pairs = []
    for team1 in possible_teams:
        for team2 in possible_teams:
            if team1 != team2:
                team_pairs.append((team1, team2))
    
    for team1, team2 in tqdm(team_pairs, desc='Calculating stats'):
        # Load teams with their stats
        attacker_dinos = []
        for dino in team1:
            dino_stats = calculate_total_stats(dino)
            attacker_dinos.append(load_dino_from_model(dino, dino_stats, 1))

        defender_dinos = []
        for dino in team2:
            dino_stats = calculate_total_stats(dino)
            defender_dinos.append(load_dino_from_model(dino, dino_stats, 2))

        team1_name = "team1"
        team2_name = "team2"

        # Start battle simulation
        battle = GameState(
            (team1_name, attacker_dinos),
            (team2_name, defender_dinos)
        )
        try:
            battle_log = battle.run()
        except :
            pass
        winner = battle.get_winner()
        
        # Update battle statistics
        log_data = json.loads(battle_log)
        
        # Get initial HP values for each dino
        initial_state = next(entry for entry in log_data if entry["type"] == "initial_state")
        dino_initial_hp = {}
        
        for team_name, team_dinos in initial_state["initial_state"].items():
            for dino in team_dinos:
                # Extract the base name without team identifier
                base_name = dino["name"]
                dino_initial_hp[dino["id"]] = {
                    "name": base_name,
                    "initial_hp": dino["current_hp"]
                }
        
        # Track when dinos died by monitoring HP in attack entries
        death_events = {}
        
        
        # Track damage, attacks for each dino
        for entry in log_data:
            if entry["type"] == "attack":
                attacker_id = entry["attacker_id"]
                defender_id = entry["defender_id"]
                attacker_name = dino_initial_hp[attacker_id]["name"]
                defender_name = dino_initial_hp[defender_id]["name"]
                damage = entry["damage"]
                
                # Check if this attack resulted in death
                if entry["defender_hp"] <= 0 and defender_name not in death_events:
                    death_events[defender_name] = entry["tick"]

                # Update attacker stats
                if attacker_name in fight_stats:
                    fight_stats[attacker_name]["dmg"] += damage
                    fight_stats[attacker_name]["attacks"] += 1
                
                # Update defender stats
                if defender_name in fight_stats:
                    fight_stats[defender_name]["hp_lost"] += damage
        
        # Update final HP and win/loss stats
        final_state = next(entry for entry in log_data if entry["type"] == "final_state")
        
        # Map team names to actual team lists for easy reference
        team_lookup = {
            team1_name: [dino.dino.name for dino in team1],
            team2_name: [dino.dino.name for dino in team2]
        }
        
        # Determine winning and losing teams
        winning_team_name = final_state.get("winner")
        
        # Track battle duration (last tick)
        last_tick = max(entry.get("tick", 0) for entry in log_data if "tick" in entry)
        
        if winning_team_name:
            winning_team = team_lookup[winning_team_name]
            losing_team = team_lookup[team2_name if winning_team_name == team1_name else team1_name]
            
            # Update wins/losses
            for dino_name in winning_team:
                if dino_name in fight_stats:
                    fight_stats[dino_name]["wins"] += 1
                    fight_stats[dino_name]["battles"] += 1
            
            for dino_name in losing_team:
                if dino_name in fight_stats:
                    fight_stats[dino_name]["losses"] += 1
                    fight_stats[dino_name]["battles"] += 1
                    
        # Update final HP values
        for team_name, team_dinos in final_state["final_state"].items():
            for dino in team_dinos:
                base_name = dino["name"]
                if base_name in fight_stats:
                    if dino["current_hp"] <= 0:
                        fight_stats[base_name]["deaths"] += 1
                        # If this dino died, record that its death was associated with a loss
                        if base_name in death_events:
                            fight_stats[base_name]["lost_when_dead"] += 1
                            fight_stats[base_name]["death_ticks"].append(death_events[base_name])
                            fight_stats[base_name]["battle_durations"].append(last_tick)
                            ticks_missed = last_tick - death_events[base_name]
                            interval_name = "0-200" if ticks_missed < 200 else "200-300" if ticks_missed < 300 else "300-400" if ticks_missed < 400 else "400-500" if ticks_missed < 500 else "500-600" if ticks_missed < 600 else "600-+"
                            fight_stats[base_name]["interval_stats"][interval_name]['deaths'] += 1
                            if winning_team_name != team_name:
                                fight_stats[base_name]["interval_stats"][interval_name]['losses'] += 1
                    else:
                        # Only accumulate HP when dino is alive
                        fight_stats[base_name]["hp_left"] += dino["current_hp"]
                        fight_stats[base_name]["hp_left_count"] += 1
    
    # Create a list to store data for DataFrame
    df_data = []
    

    # Print out the aggregated stats
    for dino_name, stats in fight_stats.items():
        if stats["battles"] > 0:
            print(f"{dino_name} Stats:")
            print(f"  Battles: {stats['battles']}")
            print(f"  Win Rate: {stats['wins']/stats['battles']*100:.2f}% | {stats['wins']} wins, {stats['losses']} losses")
            print(f"  Avg Damage: {stats['dmg']/stats['battles']:.2f}")
            print(f"  Avg HP Lost: {stats['hp_lost']/stats['battles']:.2f}")
            print(f"  Deaths: {stats['deaths']} | {stats['deaths']/stats['battles']*100:.2f}%")
            # Calculate average HP left only for battles where the dino survived
            avg_hp_left = stats['hp_left']/max(1, stats['hp_left_count']) if stats['hp_left_count'] > 0 else 0
            print(f"  Avg HP Left (when alive): {avg_hp_left:.2f}")
            
            # Calculate impact score
            impact_score = 0
            # Categorize deaths and losses by interval
            for interval, interval_stat in stats["interval_stats"].items():
                deaths = interval_stat['deaths']
                losses = interval_stat['losses']
                if deaths > 0:
                    interval_stat['ratio'] = losses / deaths
                    print(f"{interval} Death impact : {interval_stat['ratio']:.2f} | {deaths} deaths, {losses} losses")
                    impact_score += interval_stat['ratio'] * interval_stat['weight']
                else:
                    impact_score += interval_stat['weight']
            
            # Add impact score metrics if available
            if stats['deaths'] > 0:
                print(f"  Impact Score: {impact_score:.2f}")

            print("------------------------")
            
            # Collect data for DataFrame
            row_data = {
                'Dino': dino_name,
                'Battles': stats['battles'],
                'Win Rate (%)': round(stats['wins']/stats['battles']*100,2),
                'Wins': stats['wins'],
                'Losses': stats['losses'],
                'Avg Damage': int(stats['dmg']/stats['battles']),
                'Avg HP Lost': int(stats['hp_lost']/stats['battles']),
                'Deaths': stats['deaths'],
                'Death Rate (%)': round(stats['deaths']/stats['battles']*100,2),
                'Avg HP Left (when alive)': avg_hp_left,
                'Impact Score': round(impact_score, 2),
            }
            
            df_data.append(row_data)
    
    # Create and print DataFrame
    if df_data:
        stats_df = pd.DataFrame(df_data)
        print("\nDinosaur Statistics Summary:")
        print(stats_df.to_string())
        
        # Optionally save to CSV
        # stats_df.to_csv('dinosaur_stats.csv', index=False)


