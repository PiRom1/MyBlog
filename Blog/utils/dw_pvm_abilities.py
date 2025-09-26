"""
DW PvM Abilities Implementation

This module implements advanced PvM abilities that require special mechanics
beyond simple stat modifications. These abilities are applied during battle
execution rather than in stat calculation.

Currently handles team abilities:
- "Dernier souffle": When an ally dies, others recover 20% HP immediately
- "Sprint préhistorique": +20% SPD to whole team for first 5 seconds of battle
- "Esprit de meute": +20% ATK if all allies alive, -10% otherwise
- "Bouclier collectif": 50% of damage received is shared among all other living allies
- "Instinct protecteur": +30% DEF for 2s when any team member takes a critical hit
- "Pression croissante": +5% ATK every 3 seconds
- "Seul contre tous": +25% all stats when only one dino remains alive
- "Terreur collective": +15% ATK permanently when an enemy dies
- "Mort-vivant": When the first dino dies, it continues attacking for 2s without being targetable

Individual dino abilities:
- "Frénésie": +25% attack speed when HP < 50%
- "Boureau": Probability-based instant kill based on target's remaining HP
- "Peau dure": 20% damage reduction when HP > 50%
- "Inspiration héroïque": +25% ATK for all allies for 1s on critical hit
- "Vol de vie": Heals attacker for 30% of damage dealt after each attack
- "Provocation": This dino is 2x more likely to be targeted by enemies
- "Agilitée accrue": 20% chance to dodge attacks when this dino is attacked
- "Regard pétrifiant": Always reduces target's speed by 25% for 3s after attacking
- "Régénération": Every 2 seconds, heals for 5% of maximum HP
- "Chasseur nocturne": 2x damage against enemies with poison/bleed
- "Carapace robuste": Starts at 50% damage reduction, decreases by 3% per hit (min -25%)
"""

import random


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
    Sprint préhistorique ability: +20% SPD to whole team for first 5 seconds (500 ticks)
    
    Args:
        team_dinos: List of all dinos in the team
        game_state: Current game state
    """
    team_modifiers = {}
    for dino in team_dinos:
        speed_modifier = round(dino.stats.speed * 0.20, 2)
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
        from Blog.models import DWPvmRunAbility, DWPvmRun
        
        try:
            # Get abilities for this dino based on the original run ID
            run_object = DWPvmRun.objects.get(id=game_state.run_id)
            
            # Get abilities for this PvM dino
            abilities = DWPvmRunAbility.objects.filter(run=run_object).select_related('ability')
            for ability in abilities:
                for dino in team_dinos:
                    if ability.ability.name not in team_abilities:
                        team_abilities[ability.ability.name] = []
                    team_abilities[ability.ability.name].append(dino)
        except Exception as e:
            # In case of any database access issues, continue
            pass
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
    
    # Apply Esprit de meute if any dino has it
    if "Esprit de meute" in team_abilities:
        apply_esprit_de_meute(team_dinos, game_state)
    
    # Apply Pression croissante if any dino has it
    if "Pression croissante" in team_abilities:
        apply_pression_croissante(team_dinos, game_state)


def apply_individual_abilities_on_battle_start(team_dinos, game_state):
    """
    Apply individual dino abilities that trigger at battle start
    
    Args:
        team_dinos: List of dinos in the team
        game_state: Current game state
    """
    for dino in team_dinos:
        dino_abilities = get_dino_abilities(dino, game_state)
        
        # Apply Régénération if the dino has it
        if "Régénération" in dino_abilities:
            apply_regeneration_start(dino, game_state)
        
        # Apply Carapace robuste if the dino has it
        if "Carapace robuste" in dino_abilities:
            apply_carapace_robuste_start(dino, game_state)


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
    
    # Apply Mort-vivant if any dino has it (team ability now)
    if "Mort-vivant" in team_abilities:
        apply_mort_vivant(dead_dino, team_dinos, game_state)
    
    # Apply Esprit de meute if any dino has it (need to recalculate since team composition changed)
    if "Esprit de meute" in team_abilities:
        apply_esprit_de_meute(team_dinos, game_state, check_only=True)
    
    # Apply Seul contre tous if any dino has it
    if "Seul contre tous" in team_abilities:
        apply_seul_contre_tous(team_dinos, game_state)


def apply_team_abilities_on_enemy_death(enemy_dino, team_dinos, game_state):
    """
    Apply team-wide abilities that trigger when an enemy dies
    
    Args:
        enemy_dino: The enemy dino that just died
        team_dinos: List of all dinos in the team (not the enemy team)
        game_state: Current game state
    """
    team_abilities = get_team_abilities(team_dinos, game_state)
    
    # Apply Terreur collective if any dino has it
    if "Terreur collective" in team_abilities:
        apply_terreur_collective(team_dinos, game_state)


# ------------------------- INDIVIDUAL DINO ABILITIES ------------------------- #

def apply_mort_vivant(dead_dino, team_dinos, game_state):
    """
    Mort-vivant ability: When the first dino dies, it continues to attack for 2 seconds 
    without being targetable. This is now a team ability.
    
    Args:
        dead_dino: The dino that just died
        team_dinos: List of all dinos in the same team
        game_state: Current game state
    """
    # Check if this is the first death for this team
    if not hasattr(game_state, '_mort_vivant_used'):
        game_state._mort_vivant_used = set()
    
    # Get team identifier based on the dead dino
    team_id = None
    for team_name, team_dinos_list in game_state.teams.items():
        if dead_dino in team_dinos_list:
            team_id = team_name
            break
    
    if team_id is None or team_id in game_state._mort_vivant_used:
        return  # Team not found or already used mort-vivant
    
    # Mark as used for this team
    game_state._mort_vivant_used.add(team_id)
    
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


def apply_vol_de_vie(attacker, damage, game_state):
    """
    Vol de vie ability: After each attack, this dino heals for 30% of damage dealt
    
    Args:
        attacker: The dino with Vol de vie ability
        damage: The damage that was just dealt
        game_state: Current game state
    """
    if damage > 0:  # Only heal if damage was actually dealt
        heal_amount = int(damage * 0.3)
        attacker.current_hp = min(attacker.stats.hp, attacker.current_hp + heal_amount)
        game_state.log_effect("vol_de_vie", attacker, "hp", heal_amount)


def apply_frenesie(dino, game_state):
    """
    Frénésie ability: +25% attack speed when this dino's HP drops below 50%
    
    Args:
        dino: The dino to check for Frénésie
        game_state: Current game state
    """
    hp_percentage = dino.current_hp / dino.stats.hp
    
    if hp_percentage < 0.5 and "frenesie" not in dino.current_statuses:
        # Apply frénésie buff
        speed_boost = dino.stats.speed * 0.25
        dino.stats.speed += speed_boost
        dino.current_statuses.append("frenesie")
        game_state.log_effect("frenesie_start", dino, "speed", speed_boost)
        
        # Store the boost amount for later removal
        dino._frenesie_boost = speed_boost
        
    elif hp_percentage >= 0.5 and "frenesie" in dino.current_statuses:
        # Remove frénésie buff if HP goes back above 50%
        if hasattr(dino, '_frenesie_boost'):
            speed_boost = dino._frenesie_boost
            dino.stats.speed -= speed_boost
            delattr(dino, '_frenesie_boost')
            game_state.log_effect("frenesie_end", dino, "speed", -speed_boost)
        dino.current_statuses.remove("frenesie")


def apply_boureau(attacker, defender, damage, game_state):
    """
    Boureau ability: When attacking, the more target's remaining HP is low, 
    the more chances this dino have to kill the target instantly 
    Formula: (1-(remaining HP/total HP)^2)/1.1
    
    Args:
        attacker: The dino with Boureau ability
        defender: The target dino
        damage: The damage that was just dealt
        game_state: Current game state
    """
    if defender.current_hp > 0:
        # Calculate execution probability based on remaining HP percentage
        hp_percentage = defender.current_hp / defender.stats.hp
        execution_chance = (1 - hp_percentage) ** 2 / 1.1
        
        if random.random() < execution_chance:
            # Instant kill
            defender.current_hp = 0
            game_state.log_effect("boureau_execute", defender, "hp", -defender.current_hp)


def apply_peau_dure_defense(dino, damage, game_state):
    """
    Peau dure ability: While this dino has more than 50% HP, it reduces damage taken by 20%
    
    Args:
        dino: The dino with Peau dure ability
        damage: The original damage amount
        game_state: Current game state
        
    Returns:
        int: The modified damage amount
    """
    hp_percentage = dino.current_hp / dino.stats.hp
    
    if hp_percentage > 0.5:
        # Reduce damage by 20%
        reduced_damage = int(damage * 0.8)
        damage_reduction = damage - reduced_damage
        game_state.log_effect("peau_dure", dino, "damage_reduction", damage_reduction)
        return reduced_damage
    
    return damage


def apply_inspiration_heroique(attacker, team_dinos, game_state):
    """
    Inspiration héroïque ability: If this dino lands a critical hit, 
    all allies gain +25% ATK for 1 second
    
    Args:
        attacker: The dino that landed the critical hit
        team_dinos: List of all dinos in the team
        game_state: Current game state
    """
    team_modifiers = {}
    
    for dino in team_dinos:
        if dino.is_alive():
            atk_boost = int(dino.stats.atk * 0.25)
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
    
    # Apply Vol de vie if the attacker has it
    if "Vol de vie" in attacker_abilities:
        apply_vol_de_vie(attacker, damage, game_state)
    
    # Apply Boureau if the attacker has it
    if "Boureau" in attacker_abilities:
        apply_boureau(attacker, defender, damage, game_state)
    
    # Apply Regard pétrifiant if the attacker has it
    if "Regard pétrifiant" in attacker_abilities:
        apply_regard_petrifiant(attacker, defender, game_state)
    
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
    
    # Apply Carapace robuste if the defender has it
    if "Carapace robuste" in defender_abilities:
        damage = apply_carapace_robuste_damage_reduction(defender, damage, game_state)
    
    return damage


def apply_individual_abilities_on_being_attacked(defender, game_state):
    """
    Apply individual dino abilities that trigger when being attacked (before damage calculation)
    
    Args:
        defender: The dino being attacked
        game_state: Current game state
        
    Returns:
        bool: True if the attack should be dodged
    """
    defender_abilities = get_dino_abilities(defender, game_state)
    
    # Apply Agilitée accrue if the defender has it
    if "Agilitée accrue" in defender_abilities:
        return apply_agilite_accrue_dodge(defender, game_state)
    
    return False


def apply_individual_abilities_before_attack(attacker, defender, game_state):
    """
    Apply individual dino abilities that modify attack parameters before damage calculation
    
    Args:
        attacker: The attacking dino
        defender: The defending dino
        game_state: Current game state
        
    Returns:
        dict: Dictionary with modified attack parameters (e.g., {'damage_multiplier': 2.0})
    """
    attacker_abilities = get_dino_abilities(attacker, game_state)
    modifications = {}
    
    # Apply Chasseur nocturne if the attacker has it
    if "Chasseur nocturne" in attacker_abilities:
        damage_multiplier = apply_chasseur_nocturne_damage_bonus(attacker, defender, game_state)
        if damage_multiplier > 1.0:
            modifications['damage_multiplier'] = damage_multiplier
    
    return modifications


def apply_team_abilities_on_damage_taken(defender, damage, is_crit, game_state):
    """
    Apply team-wide abilities that trigger when taking damage
    
    Args:
        defender: The dino taking damage
        damage: The damage amount
        is_crit: Whether it was a critical hit
        game_state: Current game state
        
    Returns:
        int: The modified damage amount
    """
    # Find the defender's team
    defender_team = None
    for name, team in game_state.teams.items():
        if defender in team:
            defender_team = team
            defender_team_name = name
            break

    if defender_team_name != "team_joueur":
        return damage
    
    team_abilities = get_team_abilities(defender_team, game_state)
    
    # Apply Bouclier collectif if any dino has it
    if "Bouclier collectif" in team_abilities:
        damage = apply_bouclier_collectif(defender, damage, defender_team, game_state)
    
    # Apply Instinct protecteur if any dino has it and this was a critical hit
    if "Instinct protecteur" in team_abilities and is_crit:
        apply_instinct_protecteur(defender_team, game_state)
    
    return damage


def apply_individual_abilities_on_death(dead_dino, team_dinos, game_state):
    """
    Apply individual dino abilities that trigger when a dino dies
    
    Args:
        dead_dino: The dino that just died
        team_dinos: List of all dinos in the same team
        game_state: Current game state
    """
    # Check for individual dino abilities on the dead dino
    dino_abilities = get_dino_abilities(dead_dino, game_state)
    
    # Individual death abilities would go here (none currently)


# ------------------------- NEW TEAM ABILITIES ------------------------- #

def apply_esprit_de_meute(team_dinos, game_state, check_only=False):
    """
    Esprit de meute ability: +20% ATK if all allies are alive, -10% otherwise
    
    Args:
        team_dinos: List of all dinos in the team
        game_state: Current game state
        check_only: If True, only checks and applies current state without logging initial state
    """
    all_alive = all(dino.is_alive() for dino in team_dinos)
    
    # Remove any existing esprit de meute effects first
    for dino in team_dinos:
        if "esprit_de_meute" in dino.current_statuses:
            if hasattr(dino, '_esprit_de_meute_modifier'):
                dino.stats.atk -= dino._esprit_de_meute_modifier
                delattr(dino, '_esprit_de_meute_modifier')
            dino.current_statuses.remove("esprit_de_meute")
    
    # Apply new modifier based on current team state
    modifier = 0.2 if all_alive else -0.1
    for dino in team_dinos:
        if dino.is_alive():
            # Store original ATK if not already stored
            if not hasattr(dino, '_original_atk'):
                dino._original_atk = dino.stats.atk
            
            # Calculate modifier based on original ATK
            atk_modifier = int(dino._original_atk * modifier)
            dino.stats.atk += atk_modifier
            dino._esprit_de_meute_modifier = atk_modifier
            dino.current_statuses.append("esprit_de_meute")
            game_state.log_effect("esprit_de_meute", dino, "atk", atk_modifier)


def apply_bouclier_collectif(defender, damage, team_dinos, game_state):
    """
    Bouclier collectif ability: 50% of damage received is shared equally among all other living allies
    
    Args:
        defender: The dino taking the original damage
        damage: The damage amount
        team_dinos: List of all dinos in the team
        game_state: Current game state
        
    Returns:
        int: The modified damage for the original target
    """
    alive_allies = [dino for dino in team_dinos if dino.is_alive() and dino.id != defender.id]
    
    if not alive_allies:
        return damage  # No allies to share with
    
    shared_damage = int(damage * 0.5)
    damage_per_ally = shared_damage // len(alive_allies)
    remaining_damage = damage - shared_damage
    
    # Apply shared damage to allies
    for ally in alive_allies:
        ally.current_hp -= damage_per_ally
        game_state.log_effect("bouclier_collectif_share", ally, "hp", damage_per_ally)
    
    game_state.log_effect("bouclier_collectif_reduce", defender, "damage_reduction", shared_damage)
    return remaining_damage


def apply_instinct_protecteur(team_dinos, game_state):
    """
    Instinct protecteur ability: When a team member takes a critical hit, 
    the whole team gains +30% DEF for 2 seconds
    
    Args:
        team_dinos: List of all dinos in the team
        game_state: Current game state
    """
    team_modifiers = {}
    
    for dino in team_dinos:
        if dino.is_alive():
            def_boost = int(dino.stats.defense * 0.3)
            team_modifiers[dino.id] = def_boost
            dino.stats.defense += def_boost
            game_state.log_effect("instinct_protecteur_buff", dino, "defense", def_boost)
    
    def remove_instinct_buff():
        """Remove the defense buff after 2 seconds"""
        for dino in team_dinos:
            if dino.id in team_modifiers and dino.is_alive():
                dino.stats.defense -= team_modifiers[dino.id]
                game_state.log_effect("instinct_protecteur_debuff", dino, "defense", -team_modifiers[dino.id])
    
    # Schedule removal after 2 seconds (200 ticks)
    game_state.schedule_action(200, 2, remove_instinct_buff, "instinct_protecteur", None, "remove_buff")


def apply_pression_croissante(team_dinos, game_state):
    """
    Pression croissante ability: Every 3 seconds, the team's ATK increases by +5%
    
    Args:
        team_dinos: List of all dinos in the team
        game_state: Current game state
    """
    for dino in team_dinos:
        if dino.is_alive():
            atk_boost = int(dino.stats.atk * 0.05)
            dino.stats.atk += atk_boost
            game_state.log_effect("pression_croissante", dino, "atk", atk_boost)
    
    # Schedule the next application in 3 seconds (300 ticks)
    def schedule_next_pression():
        # Check if battle is still ongoing
        if all(any(d.is_alive() for d in team) for team in game_state.teams.values()):
            apply_pression_croissante(team_dinos, game_state)
    
    game_state.schedule_action(300, 2, schedule_next_pression, "pression_croissante", None, "next_boost")


def apply_seul_contre_tous(team_dinos, game_state):
    """
    Seul contre tous ability: When only one dino remains alive, it gains +25% in all stats
    
    Args:
        team_dinos: List of all dinos in the team
        game_state: Current game state
    """
    alive_dinos = [dino for dino in team_dinos if dino.is_alive()]
    
    # Apply buff if only one dino is alive
    if len(alive_dinos) == 1:
        last_dino = alive_dinos[0]
        
        # Store original stats if not already stored
        if not hasattr(last_dino, '_seul_contre_tous_applied'):
            hp_boost = int(last_dino.stats.hp * 0.25)
            atk_boost = int(last_dino.stats.atk * 0.25)
            def_boost = int(last_dino.stats.defense * 0.25)
            spd_boost = last_dino.stats.speed * 0.25
            crit_boost = 0.25
            crit_dmg_boost = last_dino.stats.crit_damage * 0.25
            
            # Apply all stat boosts
            last_dino.stats.hp += hp_boost
            last_dino.current_hp += hp_boost  # Also boost current HP
            last_dino.stats.atk += atk_boost
            last_dino.stats.defense += def_boost
            last_dino.stats.speed += spd_boost
            last_dino.stats.crit_chance += crit_boost
            last_dino.stats.crit_damage += crit_dmg_boost
            
            # Store modifiers for potential removal (though it's permanent)
            last_dino._seul_contre_tous_modifiers = {
                'hp': hp_boost, 'atk': atk_boost, 'defense': def_boost,
                'speed': spd_boost, 'crit': crit_boost, 'crit_dmg': crit_dmg_boost
            }
            last_dino._seul_contre_tous_applied = True
            last_dino.current_statuses.append("seul_contre_tous")
            
            game_state.log_effect("seul_contre_tous", last_dino, "all_stats", 0.25)


def apply_terreur_collective(team_dinos, game_state):
    """
    Terreur collective ability: When an enemy dies, the whole team gains +15% ATK until the end of battle
    
    Args:
        team_dinos: List of all dinos in the team
        game_state: Current game state
    """
    for dino in team_dinos:
        if dino.is_alive():
            atk_boost = int(dino.stats.atk * 0.15)
            dino.stats.atk += atk_boost
            game_state.log_effect("terreur_collective", dino, "atk", atk_boost)


# ------------------------- NEW INDIVIDUAL ABILITIES ------------------------- #

def apply_agilite_accrue_dodge(dino, game_state):
    """
    Agilitée accrue ability: When this dino is attacked, it has 20% chance to dodge
    This should be checked during damage calculation.
    
    Args:
        dino: The dino with Agilitée accrue ability
        game_state: Current game state
        
    Returns:
        bool: True if the attack should be dodged
    """
    if random.random() < 0.2:  # 20% chance
        game_state.log_effect("agilite_accrue_dodge", dino, "dodge", 1)
        return True
    return False


def apply_regard_petrifiant(attacker, defender, game_state):
    """
    Regard pétrifiant ability: After attacking, reduce target's speed by 25% for 3 seconds
    Effects can stack for multiple applications.
    
    Args:
        attacker: The dino with Regard pétrifiant ability
        defender: The target dino
        game_state: Current game state
    """
    # Store original speed if not already stored for this effect
    if not hasattr(defender, '_regard_petrifiant_original_speed'):
        defender._regard_petrifiant_original_speed = defender.stats.speed
    
    # Apply speed reduction (25% of original speed) - effects can stack
    speed_reduction = defender._regard_petrifiant_original_speed * 0.25
    defender.stats.speed -= speed_reduction
    
    # Track multiple stacks for restoration
    if not hasattr(defender, '_regard_petrifiant_stacks'):
        defender._regard_petrifiant_stacks = []
    
    stack_id = len(defender._regard_petrifiant_stacks)
    defender._regard_petrifiant_stacks.append(speed_reduction)
    
    # Add status and log
    if "regard_petrifiant" not in defender.current_statuses:
        defender.current_statuses.append("regard_petrifiant")
    game_state.log_effect("regard_petrifiant", defender, "speed", -speed_reduction)
    
    def restore_speed():
        if hasattr(defender, '_regard_petrifiant_stacks') and stack_id < len(defender._regard_petrifiant_stacks):
            # Restore this specific stack
            stack_reduction = defender._regard_petrifiant_stacks[stack_id]
            defender.stats.speed += stack_reduction
            defender._regard_petrifiant_stacks[stack_id] = 0  # Mark as restored
            game_state.log_effect("regard_petrifiant_restore", defender, "speed", stack_reduction)
            
            # Remove status only if all stacks are restored
            if all(stack == 0 for stack in defender._regard_petrifiant_stacks):
                if "regard_petrifiant" in defender.current_statuses:
                    defender.current_statuses.remove("regard_petrifiant")
    
    # Schedule restoration after 3 seconds (300 ticks)
    game_state.schedule_action(300, 2, restore_speed, "regard_petrifiant", defender.id, f"restore_regard_petrifiant_{stack_id}")


def apply_regeneration_start(dino, game_state):
    """
    Régénération ability: Every 2 seconds, heals for 5% of maximum HP
    This should be called once at battle start to begin the regeneration cycle.
    
    Args:
        dino: The dino with Régénération ability
        game_state: Current game state
    """
    def regenerate():
        if dino.is_alive():
            heal_amount = int(dino.stats.hp * 0.05)
            dino.current_hp = min(dino.stats.hp, dino.current_hp + heal_amount)
            game_state.log_effect("regeneration", dino, "hp", heal_amount)
            
            # Schedule next regeneration in 2 seconds (200 ticks)
            game_state.schedule_action(200, 2, regenerate, "regeneration", dino.id, "regenerate")
    
    # Start the first regeneration after 2 seconds
    game_state.schedule_action(200, 2, regenerate, "regeneration", dino.id, "regenerate")


def apply_chasseur_nocturne_damage_bonus(attacker, defender, game_state):
    """
    Chasseur nocturne ability: Deals 2x damage against enemies afflicted with status effects (poison & bleed)
    
    Args:
        attacker: The dino with Chasseur nocturne ability
        defender: The target dino
        game_state: Current game state
        
    Returns:
        float: Damage multiplier (1.0 for normal, 2.0 for status-affected enemies)
    """
    if "poison" in defender.current_statuses or "bleed" in defender.current_statuses:
        game_state.log_effect("chasseur_nocturne", attacker, "damage_bonus", 2.0)
        return 2.0
    return 1.0


def apply_carapace_robuste_start(dino, game_state):
    """
    Carapace robuste ability: Starts each fight at 50% damage reduction. 
    Damage reduction drops by 3% each time this dino takes damage (can go negative down to -25%).
    This should be called once at battle start.
    
    Args:
        dino: The dino with Carapace robuste ability
        game_state: Current game state
    """
    dino._carapace_robuste_resist = 0.5  # Start at 50% damage reduction
    dino.current_statuses.append("carapace_robuste")
    game_state.log_effect("carapace_robuste_start", dino, "damage_resist", 0.5)


def apply_carapace_robuste_damage_reduction(dino, damage, game_state):
    """
    Carapace robuste ability: Apply current damage resistance and then reduce it by 3%.
    Minimum resistance is -25% (meaning 25% extra damage).
    
    Args:
        dino: The dino with Carapace robuste ability
        damage: The original damage amount
        game_state: Current game state
        
    Returns:
        int: The modified damage amount after resistance
    """
    if not hasattr(dino, '_carapace_robuste_resist'):
        return damage
    
    # Apply current resistance
    resistance = dino._carapace_robuste_resist
    if resistance > 0:
        reduced_damage = int(damage * (1 - resistance))
        damage_blocked = damage - reduced_damage
        game_state.log_effect("carapace_robuste_block", dino, "damage_blocked", damage_blocked)
    else:
        # Negative resistance means extra damage
        extra_damage = int(damage * abs(resistance))
        reduced_damage = damage + extra_damage
        game_state.log_effect("carapace_robuste_amplify", dino, "extra_damage", extra_damage)
    
    # Reduce resistance by 3% (0.03) for next hit, minimum -25%
    dino._carapace_robuste_resist = max(-0.25, dino._carapace_robuste_resist - 0.03)
    game_state.log_effect("carapace_robuste_degrade", dino, "damage_resist", dino._carapace_robuste_resist)
    
    return max(0, reduced_damage)