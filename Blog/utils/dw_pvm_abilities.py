"""
DW PvM Abilities Implementation

This module implements advanced PvM abilities that require special mechanics
beyond simple stat modifications. These abilities are applied during battle
execution rather than in stat calculation.

Currently handles:
- "Dernier souffle": When an ally dies, others recover 20% HP immediately
- "Sprint préhistorique": +15% SPD to whole team for first 5 seconds of battle

New individual dino abilities:
- "Mort-vivant": Continue attacking for 2s after death without being targetable
- "Frénésie": +20% attack speed when HP < 30%
- "Boureau": Instant kill if target's remaining HP < damage dealt
- "Peau dure": 15% damage reduction when HP > 70%
- "Inspiration héroïque": +20% ATK for all allies for 1s on critical hit
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
    team_abilities = {}
    
    try:
        # Import here to avoid circular imports
        from Blog.models import DWPvmRunAbility, DWPvmDino
        
        for dino in team_dinos:
            try:
                # Get abilities for this dino based on the original dino ID
                # The battle dino ID might be modified with team_identifier
                original_dino_id = dino.id
                if original_dino_id > 1000:
                    original_dino_id = original_dino_id // 1000
                
                # Find the DWPvmDino object that corresponds to this battle dino
                pvm_dino = DWPvmDino.objects.get(id=original_dino_id)
                
                # Get abilities for this PvM dino
                abilities = DWPvmRunAbility.objects.filter(dino=pvm_dino).select_related('ability')
                for ability in abilities:
                    ability_name = ability.ability.name
                    if ability_name not in team_abilities:
                        team_abilities[ability_name] = []
                    team_abilities[ability_name].append(dino)
            except Exception as e:
                # In case of any database access issues, continue
                continue
    except ImportError:
        # Django models not available (e.g., in testing environment)
        pass
    except Exception as e:
        # Any other database-related errors
        pass
    
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


# ------------------------- INDIVIDUAL DINO ABILITIES ------------------------- #

def apply_mort_vivant(dead_dino, team_dinos, game_state):
    """
    Mort-vivant ability: When this dino dies, it continues to attack for 2 seconds 
    without being targetable (unless it's the last dino alive)
    
    Args:
        dead_dino: The dino that just died and has Mort-vivant
        team_dinos: List of all dinos in the same team
        game_state: Current game state
    """
    # Check if this is the last dino alive in the team
    alive_teammates = [dino for dino in team_dinos if dino.is_alive()]
    if len(alive_teammates) == 0:  # This was the last dino
        return
    
    # Mark the dino as "undead" and make it targetable again temporarily
    dead_dino.current_statuses.append("mort_vivant")
    dead_dino.current_hp = 1  # Set to 1 HP to make it "alive" for targeting purposes
    
    # Make the dino untargetable by adding a special status
    dead_dino.current_statuses.append("untargetable")
    
    # Schedule attacks for the next 2 seconds (200 ticks)
    interval = int(100 / dead_dino.stats.speed)
    attacks_in_2_seconds = 200 // interval
    
    for i in range(attacks_in_2_seconds):
        game_state.schedule_action(
            interval * (i + 1), 
            1, 
            lambda d=dead_dino: game_state.dino_action(d), 
            "dino_action", 
            dead_dino.id
        )
    
    # After 2 seconds, truly kill the dino
    def end_mort_vivant():
        dead_dino.current_hp = 0
        if "mort_vivant" in dead_dino.current_statuses:
            dead_dino.current_statuses.remove("mort_vivant")
        if "untargetable" in dead_dino.current_statuses:
            dead_dino.current_statuses.remove("untargetable")
        game_state.log_effect("mort_vivant_end", dead_dino, "hp", 0)
    
    game_state.schedule_action(200, 2, end_mort_vivant, "mort_vivant", dead_dino.id, "end_mort_vivant")
    game_state.log_effect("mort_vivant_start", dead_dino, "mort_vivant", 200)


def apply_frenesie(dino, game_state):
    """
    Frénésie ability: +20% attack speed when this dino's HP drops below 30%
    
    Args:
        dino: The dino to check for Frénésie
        game_state: Current game state
    """
    hp_percentage = dino.current_hp / dino.stats.hp
    
    if hp_percentage < 0.3 and "frenesie" not in dino.current_statuses:
        # Apply frénésie buff
        speed_boost = dino.stats.speed * 0.2
        dino.stats.speed += speed_boost
        dino.current_statuses.append("frenesie")
        game_state.log_effect("frenesie_start", dino, "speed", speed_boost)
        
        # Store the boost amount for later removal
        dino._frenesie_boost = speed_boost
        
    elif hp_percentage >= 0.3 and "frenesie" in dino.current_statuses:
        # Remove frénésie buff if HP goes back above 30%
        if hasattr(dino, '_frenesie_boost'):
            speed_boost = dino._frenesie_boost
            dino.stats.speed -= speed_boost
            delattr(dino, '_frenesie_boost')
            game_state.log_effect("frenesie_end", dino, "speed", -speed_boost)
        dino.current_statuses.remove("frenesie")


def apply_boureau(attacker, defender, damage, game_state):
    """
    Boureau ability: After the attack, if the target's remaining HP is lower 
    than the damage it just received, it dies instantly
    
    Args:
        attacker: The dino with Boureau ability
        defender: The target dino
        damage: The damage that was just dealt
        game_state: Current game state
    """
    if defender.current_hp > 0 and defender.current_hp < damage:
        # Instant kill
        defender.current_hp = 0
        game_state.log_effect("boureau_execute", defender, "hp", -defender.current_hp)


def apply_peau_dure_defense(dino, damage, game_state):
    """
    Peau dure ability: While this dino has more than 70% HP, it reduces damage taken by 15%
    
    Args:
        dino: The dino with Peau dure ability
        damage: The original damage amount
        game_state: Current game state
        
    Returns:
        int: The modified damage amount
    """
    hp_percentage = dino.current_hp / dino.stats.hp
    
    if hp_percentage > 0.7:
        # Reduce damage by 15%
        reduced_damage = int(damage * 0.85)
        damage_reduction = damage - reduced_damage
        game_state.log_effect("peau_dure", dino, "damage_reduction", damage_reduction)
        return reduced_damage
    
    return damage


def apply_inspiration_heroique(attacker, team_dinos, game_state):
    """
    Inspiration héroïque ability: If this dino lands a critical hit, 
    all allies gain +20% ATK for 1 second
    
    Args:
        attacker: The dino that landed the critical hit
        team_dinos: List of all dinos in the team
        game_state: Current game state
    """
    team_modifiers = {}
    
    for dino in team_dinos:
        if dino.is_alive():
            atk_boost = int(dino.stats.atk * 0.2)
            team_modifiers[dino.id] = atk_boost
            dino.stats.atk += atk_boost
            game_state.log_effect("inspiration_heroique_buff", dino, "atk", atk_boost)
    
    def remove_inspiration_buff():
        """Remove the attack buff after 1 second"""
        for dino in team_dinos:
            if dino.id in team_modifiers and dino.is_alive():
                dino.stats.atk -= team_modifiers[dino.id]
                game_state.log_effect("inspiration_heroique_debuff", dino, "atk", -team_modifiers[dino.id])
    
    # Schedule removal after 1 second (100 ticks)
    game_state.schedule_action(100, 2, remove_inspiration_buff, "inspiration_heroique", attacker.id, "remove_buff")


def get_dino_abilities(dino, game_state=None):
    """
    Get all abilities that affect a specific dino from DWPvmRunAbility objects
    
    Args:
        dino: The dino to check abilities for
        game_state: Current game state (for database access context)
    
    Returns:
        list: List of ability names that this dino has
    """
    dino_abilities = []
    
    try:
        # Import here to avoid circular imports
        from Blog.models import DWPvmRunAbility, DWPvmDino
        
        # Get the original dino ID (battle dino ID might be modified with team_identifier)
        original_dino_id = dino.id
        if original_dino_id > 1000:
            original_dino_id = original_dino_id // 1000
        
        # Find the DWPvmDino object that corresponds to this battle dino
        pvm_dino = DWPvmDino.objects.get(id=original_dino_id)
        
        # Get abilities for this PvM dino where to_dino=True (individual abilities)
        abilities = DWPvmRunAbility.objects.filter(dino=pvm_dino).select_related('ability')
        for ability in abilities:
            if ability.ability.to_dino:  # Only individual dino abilities
                dino_abilities.append(ability.ability.name)
                
    except Exception as e:
        # In case of any database access issues, continue
        pass
    
    return dino_abilities


def apply_individual_abilities_on_hp_change(dino, game_state):
    """
    Apply individual dino abilities that trigger on HP changes
    
    Args:
        dino: The dino to check abilities for
        game_state: Current game state
    """
    dino_abilities = get_dino_abilities(dino, game_state)
    
    # Apply Frénésie if the dino has it
    if "Frénésie" in dino_abilities:
        apply_frenesie(dino, game_state)


def apply_individual_abilities_on_attack(attacker, defender, damage, is_crit, game_state):
    """
    Apply individual dino abilities that trigger on attacks
    
    Args:
        attacker: The attacking dino
        defender: The defending dino
        damage: The damage dealt
        is_crit: Whether it was a critical hit
        game_state: Current game state
    """
    attacker_abilities = get_dino_abilities(attacker, game_state)
    
    # Apply Boureau if the attacker has it
    if "Boureau" in attacker_abilities:
        apply_boureau(attacker, defender, damage, game_state)
    
    # Apply Inspiration héroïque if the attacker has it and landed a crit
    if "Inspiration héroïque" in attacker_abilities and is_crit:
        # Find the attacker's team
        attacker_team = None
        for team in game_state.teams.values():
            if attacker in team:
                attacker_team = team
                break
        
        if attacker_team:
            apply_inspiration_heroique(attacker, attacker_team, game_state)


def apply_individual_abilities_on_damage_taken(defender, damage, game_state):
    """
    Apply individual dino abilities that trigger when taking damage
    
    Args:
        defender: The dino taking damage
        damage: The original damage amount
        game_state: Current game state
        
    Returns:
        int: The modified damage amount
    """
    defender_abilities = get_dino_abilities(defender, game_state)
    
    # Apply Peau dure if the defender has it
    if "Peau dure" in defender_abilities:
        damage = apply_peau_dure_defense(defender, damage, game_state)
    
    return damage
    
    # Check for individual dino abilities on the dead dino
    dino_abilities = get_dino_abilities(dead_dino, game_state)
    
    # Apply Mort-vivant if the dead dino has it
    if "Mort-vivant" in dino_abilities:
        apply_mort_vivant(dead_dino, team_dinos, game_state)