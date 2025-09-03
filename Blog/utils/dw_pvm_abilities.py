"""
DW PvM Abilities Implementation

This module implements advanced PvM abilities that require special mechanics
beyond simple stat modifications. These abilities are applied during battle
execution rather than in stat calculation.

Currently handles:
- "Dernier souffle": When an ally dies, others recover 20% HP immediately
- "Sprint préhistorique": +15% SPD to whole team for first 5 seconds of battle
"""


def apply_dernier_souffle(dead_dino, team_dinos, game_state):
    """
    Dernier souffle ability: When an ally dies, others recover 20% HP immediately
    
    Args:
        dead_dino: The dino that just died
        team_dinos: List of all dinos in the same team
        game_state: Current game state
    """
    for dino in team_dinos:
        if dino.id != dead_dino.id and dino.is_alive():
            heal_amount = int(dino.stats.hp * 0.2)
            dino.current_hp = min(dino.stats.hp, dino.current_hp + heal_amount)
            game_state.log_effect("dernier_souffle_heal", dino, "hp", heal_amount)


def apply_sprint_prehistorique(team_dinos, game_state):
    """
    Sprint préhistorique ability: +15% SPD to whole team for first 5 seconds (500 ticks)
    
    Args:
        team_dinos: List of all dinos in the team
        game_state: Current game state
    """
    team_modifiers = {}
    for dino in team_dinos:
        speed_modifier = round(dino.stats.speed * 0.15, 2)
        team_modifiers[dino.id] = speed_modifier
        dino.stats.speed += speed_modifier
        game_state.log_effect("sprint_prehistorique_buff", dino, "speed", speed_modifier)
    
    def restore_speed():
        """Remove the speed buff after 5 seconds"""
        for dino in team_dinos:
            if dino.id in team_modifiers and dino.is_alive():
                dino.stats.speed -= team_modifiers[dino.id]
                game_state.log_effect("sprint_prehistorique_debuff", dino, "speed", -team_modifiers[dino.id])
    
    # Schedule the speed restoration after 5 seconds (500 ticks)
    game_state.schedule_action(500, 2, restore_speed, "sprint_prehistorique", None, "restore_speed")


def get_team_abilities(team_dinos, game_state=None):
    """
    Get all abilities that affect a team from DWPvmRunAbility objects
    
    Args:
        team_dinos: List of dinos in the team
        game_state: Current game state (for database access context)
    
    Returns:
        dict: Dictionary mapping ability names to lists of dinos that have them
    """
    # Import here to avoid circular imports
    from Blog.models import DWPvmRunAbility
    
    team_abilities = {}
    
    for dino in team_dinos:
        try:
            # Get abilities for this dino based on the original dino ID
            # The battle dino ID might be modified with team_identifier
            original_dino_id = dino.id
            if original_dino_id > 1000:
                original_dino_id = original_dino_id // 1000
            
            abilities = DWPvmRunAbility.objects.filter(dino_id=original_dino_id).select_related('ability')
            for ability in abilities:
                ability_name = ability.ability.name
                if ability_name not in team_abilities:
                    team_abilities[ability_name] = []
                team_abilities[ability_name].append(dino)
        except Exception as e:
            # In case of any database access issues, continue
            continue
    
    return team_abilities


def apply_team_abilities_on_battle_start(team_dinos, game_state):
    """
    Apply team-wide abilities that trigger at battle start
    
    Args:
        team_dinos: List of dinos in the team
        game_state: Current game state
    """
    team_abilities = get_team_abilities(team_dinos, game_state)
    
    # Apply Sprint préhistorique if any dino has it
    if "Sprint préhistorique" in team_abilities:
        apply_sprint_prehistorique(team_dinos, game_state)


def apply_team_abilities_on_death(dead_dino, team_dinos, game_state):
    """
    Apply team-wide abilities that trigger when a dino dies
    
    Args:
        dead_dino: The dino that just died
        team_dinos: List of all dinos in the same team
        game_state: Current game state
    """
    team_abilities = get_team_abilities(team_dinos, game_state)
    
    # Apply Dernier souffle if any dino has it
    if "Dernier souffle" in team_abilities:
        apply_dernier_souffle(dead_dino, team_dinos, game_state)