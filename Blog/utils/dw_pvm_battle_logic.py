import json
import heapq
import random
from dataclasses import dataclass, field, asdict
from typing import Callable, List, Dict, Optional
from django.db.models import Model


@dataclass
class DinoStats:
    hp: int
    atk: int
    defense: int
    speed: float  # attacks per second
    crit_chance: float
    crit_damage: float
    accuracy: float = 1.0  # 100% accuracy by default
    dodge: float = 0.0  # 0% dodge chance by default


@dataclass
class Attack:
    name: str
    dmg_multiplier: tuple  # (min, max)
    on_hit_effect: Callable[['Dino', 'Dino', 'GameState'], None] = None
    before_attack_effect: Callable[['Dino', 'Dino', 'GameState'], None] = None


@dataclass
class Dino:
    id: int
    name: str
    user: str
    stats: DinoStats
    attack: Attack
    dino_class: str = "dps"  # Store the dino class for terrain effects
    current_hp: int = field(init=False)
    current_statuses: List[str] = field(default_factory=list)
    cooldown: bool = False # Indicates if the dino's attack's special effect is on cooldown

    def __post_init__(self):
        self.current_hp = int(self.stats.hp)

    def is_alive(self):
        # Special case for Mort-vivant: dino is considered alive if it has mort_vivant status
        if "mort_vivant" in self.current_statuses:
            return True
        return self.current_hp > 0


@dataclass(order=True)
class ScheduledAction:
    tick: int
    priority: int
    action: Callable[[], None] = field(compare=False)
    action_type: str = field(default="generic", compare=False)
    dino_id: int = field(default=None, compare=False)  # ID of the dino
    effect_name: str = field(default=None, compare=False)  # Name of the effect (if applicable)


class GameState:
    def __init__(self, team1: tuple[str, List[Dino]], team2: tuple[str, List[Dino]], terrain: str = None, run_id: int = 0):
        self.run_id = run_id
        self.teams = {team1[0]: team1[1], team2[0]: team2[1]}
        self.terrain = terrain
        self.tick = 0
        self.action_queue: List[ScheduledAction] = []
        self.fight_log: List[Dict] = []
        self.log_initial_state()

    def log_initial_state(self):
        initial_state = {
            "type": "initial_state",
            "tick": 0,
            "initial_state": {
                team_name: [self._get_serializable_dino(dino) for dino in dinos]
                for team_name, dinos in self.teams.items()
            }
        }
        self.fight_log.append(initial_state)

    def schedule_action(self, tick_delay: int, priority: int, action: Callable[[], None], 
                  action_type: str = "generic", dino_id: int = None, effect_name: str = None):
        heapq.heappush(self.action_queue, ScheduledAction(
                self.tick + tick_delay, 
                priority, 
                action,
                action_type,
                dino_id,
                effect_name
            )
        )

    def run(self):
        # Apply team abilities on battle start
        from Blog.utils.dw_pvm_abilities import apply_team_abilities_on_battle_start, apply_individual_abilities_on_battle_start    
        apply_team_abilities_on_battle_start(self.teams['team_joueur'], self)
        apply_individual_abilities_on_battle_start(self.teams['team_joueur'], self)

        # Schedule initial attacks for all dinos
        for team_name, dinos in self.teams.items():
            for dino in dinos:
                interval = int(100 / dino.stats.speed)
                self.schedule_action(interval, 1, lambda d=dino: self.dino_action(d), "dino_action", dino.id)

        if self.terrain == "Lac Putréfié":
            self.schedule_action(100, 1, self.lac_putrefie, "lac_putrefie", None, None)

        while self.action_queue and all(any(d.is_alive() for d in team) for team in self.teams.values()) and self.tick < 10000:
            print("Tick:", self.tick, "Next action tick:", self.action_queue[0].tick, "Queue length:", len(self.action_queue))
            next_tick = self.action_queue[0].tick
            self.tick = next_tick

            actions_this_tick = []
            while self.action_queue and self.action_queue[0].tick == next_tick:
                actions_this_tick.append(heapq.heappop(self.action_queue))

            for action in actions_this_tick:
                action.action()

        # Log final state, export fight log, and return results
        final_state = {
            "type": "final_state",
            "tick": self.tick,
            "final_state": {
                team_name: [self._get_serializable_dino(dino) for dino in dinos]
                for team_name, dinos in self.teams.items()
            },
            "winner": self.get_winner(),
        }
        self.fight_log.append(final_state)
        return json.dumps(self.fight_log, indent=2)

    def dino_action(self, attacker: Dino, defender: Dino = None):
        if not attacker.is_alive():
            return
        
        if defender is None:
            defender = self.choose_target(attacker)
        # If no valid target was found, schedule the attack for later and exit safely
        if defender is None:
            interval = int(100 / attacker.stats.speed)
            already_scheduled = False
            for action in self.action_queue:
                if action.action_type == "dino_action" and action.dino_id == attacker.id:
                    already_scheduled = True
                    break
            if not already_scheduled:
                self.schedule_action(interval, 1, lambda d=attacker: self.dino_action(d), "dino_action", attacker.id)
            return
        if defender.is_alive():
            do_attack = True
            miss = False
            # Apply before attack effect if any
            if attacker.attack.before_attack_effect:
                do_attack, miss = attacker.attack.before_attack_effect(attacker, defender, self)
            if do_attack:
                damage, miss = self.dino_attack(attacker, defender)
            # Apply on-hit effect if any
            if attacker.attack.on_hit_effect and not miss:
                attacker.attack.on_hit_effect(attacker, defender, self, damage)

        # Schedule next attack
        interval = int(100 / attacker.stats.speed)
        already_scheduled = False
        for action in self.action_queue:
            if action.action_type == "dino_action" and action.dino_id == attacker.id:
                already_scheduled = True
                break
        if not already_scheduled:
            self.schedule_action(interval, 1, lambda d=attacker: self.dino_action(d), "dino_action", attacker.id)

    def dino_attack(self, attacker: Dino, defender: Dino, custom_stats: tuple = None, damage: int = None, is_crit: bool = False):
        # Defensive guards: if defender is missing or either party is dead, return no-damage
        if defender is None:
            return 0, False
        if not attacker.is_alive() or not defender.is_alive():
            return 0, False
        if damage is None:
            stats = [attacker.stats.atk, attacker.attack.dmg_multiplier, defender.stats.defense, attacker.stats.crit_chance, attacker.stats.crit_damage]
            
            # Apply individual abilities that modify attack parameters before damage calculation
            from Blog.utils.dw_pvm_abilities import apply_individual_abilities_before_attack
            attack_modifications = apply_individual_abilities_before_attack(attacker, defender, self)
            
            # Apply damage multiplier (Chasseur nocturne)
            damage_multiplier = attack_modifications.get('damage_multiplier', 1.0)
            
            if custom_stats:
                for i, stat in enumerate(custom_stats):
                    if stat is not None:
                        stats[i] = stat                
            damage, is_crit = self.calculate_damage(*stats)
            
            # Apply damage multiplier after base damage calculation
            damage = int(damage * damage_multiplier)

        miss = random.random() > attacker.stats.accuracy
        
        # Check for Agilitée accrue dodge
        from Blog.utils.dw_pvm_abilities import apply_individual_abilities_on_being_attacked
        if not miss and apply_individual_abilities_on_being_attacked(defender, self):
            miss = True
        
        if "dodge" in defender.current_statuses and not miss:
            miss = random.random() < defender.stats.dodge
            defender.current_statuses.remove("dodge")
            defender.stats.dodge = 0.0  # Reset dodge chance after use
            self.log_effect("dodge", defender, "outcome", "succes" if miss else "fail")
        if miss:
            damage = 0
            is_crit = False

        else:
            if "bleed" in defender.current_statuses:
                damage = int(damage * 1.2)
            
            # Apply individual abilities that modify damage taken (Peau dure, Carapace robuste)
            from Blog.utils.dw_pvm_abilities import apply_individual_abilities_on_damage_taken, apply_team_abilities_on_damage_taken
            damage = apply_individual_abilities_on_damage_taken(defender, damage, self)
            
            # Apply team abilities that modify damage taken (Bouclier collectif, Instinct protecteur)
            damage_taken = apply_team_abilities_on_damage_taken(defender, damage, is_crit, self)

            defender.current_hp -= damage_taken
            defender.current_hp = int(defender.current_hp)

            # Apply individual abilities on HP change (Frénésie)
            from Blog.utils.dw_pvm_abilities import apply_individual_abilities_on_hp_change
            apply_individual_abilities_on_hp_change(defender, self)
            
            # Check if defender died and trigger death abilities
            if defender.current_hp <= 0 and damage_taken > 0:
                self.apply_death_effects(defender)

            log_entry = {
                "type": "attack",
                "tick": self.tick,
                "attacker": attacker.name,
                "attacker_id": attacker.id,
                "defender": defender.name,
                "defender_id": defender.id,
                "damage": damage,
                "is_crit": is_crit,
                "defender_hp": max(defender.current_hp, 0)
            }
            self.fight_log.append(log_entry)
            
            # Apply individual abilities that trigger on attacks (Bourreau, Inspiration héroïque)
            from Blog.utils.dw_pvm_abilities import apply_individual_abilities_on_attack
            apply_individual_abilities_on_attack(attacker, defender, damage, is_crit, self)
            
            if "reflect" in defender.current_statuses:
                reflected_damage = int(damage * 0.75)
                attacker.current_hp -= reflected_damage
                attacker.current_hp = int(attacker.current_hp)
                # Source is the defender returning damage to the attacker
                self.log_effect("reflect_damage", attacker, "hp", reflected_damage, source=defender)
                defender.current_statuses.remove("reflect")
                # Also check attacker's HP for Frénésie (in case of reflect damage)
                apply_individual_abilities_on_hp_change(attacker, self)

        return damage, miss

    def choose_target(self, attacker: Dino):
        enemy_team = next(team for team in self.teams.values() if attacker not in team)
        # Filter out untargetable dinos (for Mort-vivant ability)
        opponents = [d for d in enemy_team if d.is_alive() and "untargetable" not in d.current_statuses]
        
        if not opponents:
            return None
        
        # Check if any opponent has Provocation ability
        from Blog.utils.dw_pvm_abilities import get_dino_abilities
        weights = []
        
        for opponent in opponents:
            opponent_abilities = get_dino_abilities(opponent, self)
            # Dinos with Provocation are 2x more likely to be targeted
            weight = 2.0 if "Provocation" in opponent_abilities else 1.0
            weights.append(weight)
        
        # Use weighted random selection
        return random.choices(opponents, weights=weights)[0]

    def calculate_damage(self, atk: int, mult: float, defense: int, crit_chance: float, crit_damage: float) -> float:
        multiplier = random.uniform(*mult)
        base_dmg = atk * multiplier
        is_crit = random.random() < crit_chance
        if is_crit:
            base_dmg *= crit_damage
        damage_after_def = int(base_dmg) - defense
        return max(0, damage_after_def), is_crit
    
    def log_effect(self, event: str, dino: Dino, stat: str, value: float, source: Optional['Dino'] = None):
        log_entry = {
            "type": "effect",
            "tick": self.tick,
            "event": event, # event name or description
            "dino": dino.name, # dino affected
            "dino_id": dino.id,
            "stat": stat, # stat affected (e.g., "defense", "speed")
            "value": value, # modifier value (e.g., -20 for debuff, +20 for buff)
            "new_value": getattr(dino.stats, stat, None) # new value after applying the effect
        }
        if source is not None:
            log_entry["source_dino"] = source.name
            log_entry["source_dino_id"] = source.id
        self.fight_log.append(log_entry)

    def get_winner(self):
        for team_name, dinos in self.teams.items():
            if all(not dino.is_alive() for dino in dinos):
                return next(team for team in self.teams if team != team_name)
            
        # If both teams have alive dinos, return highest sum of HP
        team_hp = {team_name: sum(dino.current_hp for dino in dinos if dino.is_alive()) for team_name, dinos in self.teams.items()}
        return max(team_hp, key=team_hp.get) if team_hp else None
    
    def _get_serializable_dino(self, dino):
        dino_dict = {
            "id": dino.id,
            "name": dino.name,
            "user": dino.user,
            "dino_class": dino.dino_class,
            "stats": asdict(dino.stats),
            "current_hp": dino.current_hp,
            "current_statuses": dino.current_statuses,
            "cooldown": dino.cooldown,
            "attack": {
                "name": dino.attack.name,
                "dmg_multiplier": dino.attack.dmg_multiplier,
                # Omit function references
            }
        }
        return dino_dict
    
    def lac_putrefie(self):
        for team_name, dinos in self.teams.items():
            for dino in dinos:
                if dino.is_alive() and dino.stats.hp > 0:
                    dino.current_hp = max(0, dino.current_hp - int(dino.stats.hp * 0.05))
                    dino.current_hp = int(dino.current_hp)
                    self.log_effect("lac_putrefie", dino, "hp", -int(dino.stats.hp * 0.05))
                    if dino.current_hp == 0:
                        self.apply_death_effects(dino)
        self.schedule_action(100, 1, self.lac_putrefie, "lac_putrefie", None, None)  # Schedule next effect application

    def apply_death_effects(self, dino: Dino):
        dino_team = next(team for team in self.teams.values() if dino in team)
        from Blog.utils.dw_pvm_abilities import apply_team_abilities_on_death, apply_individual_abilities_on_death, apply_team_abilities_on_enemy_death
        
        # Apply death-triggered abilities only if dino is on the player's team
        if dino_team == self.teams['team_joueur']:
            apply_team_abilities_on_death(dino, dino_team, self)
            apply_individual_abilities_on_death(dino, dino_team, self)
        
        # Apply enemy death abilities
        else:
            for team in self.teams.values():
                if team != dino_team:
                    apply_team_abilities_on_enemy_death(dino, team, self)

# ------------------------- LOADING DINOS ------------------------- #
    
# Example of loading from Django models
def load_dino_from_model(userDino: Model, stats: Dict[str, float], team_identifier: int = None, terrain: str = None) -> Dino:
    atk_name = str(userDino.attack.name).replace(" ", "_").lower()
    dino_id = userDino.id
    user = userDino.user.username if hasattr(userDino, "user") else "Pvm_Bot"
    
    # If team_identifier is provided, create a unique ID
    if team_identifier is not None:
        dino_id = userDino.id * 1000 + team_identifier  # This ensures unique IDs across teams
    
    # Apply terrain-based stat modifications
    modified_stats = apply_terrain_stats(stats, userDino.dino.classe, terrain)
    
    return Dino(
        id=dino_id,
        name=str(userDino.dino),
        user=user,
        dino_class=userDino.dino.classe,
        stats=DinoStats(
            hp=modified_stats['hp'],
            atk=modified_stats['atk'],
            defense=modified_stats['defense'],
            speed=modified_stats['spd'],
            crit_chance=modified_stats['crit'],
            crit_damage=modified_stats['crit_dmg'],
            accuracy=0.5 if terrain == "Brouillard Epais" else 1.0,
        ),
        attack=Attack(
            name=atk_name,
            dmg_multiplier=(userDino.attack.atk_mult_low, userDino.attack.atk_mult_high),
            before_attack_effect=globals().get(f"{atk_name}_before_effect", None),
            on_hit_effect=globals().get(f"{atk_name}_effect", None)
        )
    )

def apply_terrain_stats(stats: Dict[str, float], dino_class: str, terrain: str) -> Dict[str, float]:
    """Apply terrain-based stat modifications based on dino class"""
    modified_stats = stats.copy()
    
    if terrain == "Montagne Rocheuse":
        if dino_class == "tank":
            modified_stats['defense'] = int(stats['defense'] * 1.10)  # +10% defense for tanks
        elif dino_class == "dps":
            modified_stats['atk'] = int(stats['atk'] * 0.80)  # -20% attack for DPS
    
    elif terrain == "Eruption Volcanique":
        if dino_class == "dps":
            modified_stats['atk'] = int(stats['atk'] * 1.10)  # +10% attack for DPS
        elif dino_class == "tank":
            modified_stats['defense'] = int(stats['defense'] * 0.80)  # -20% defense for tanks
    
    # Ensure integer types for core stats
    for k in ['hp', 'atk', 'defense']:
        if k in modified_stats:
            modified_stats[k] = int(modified_stats[k])
    return modified_stats

# ------------------------- TERRAIN EFFECTS ------------------------ #

# JUNGLE PERFIDE - Cooldown reduced by 20% for Support dinos
def jungle_perfide_terrain(time: int, game_state: GameState, dino: 'Dino') -> int:
    if game_state.terrain == "Jungle Perfide" and dino.dino_class == "support":
        return time - int(0.2 * time)  # 20% of the time is removed for support dinos
    return time  # No change in time for other terrains or non-support dinos

# ------------------------- ATTACK EFFECTS ------------------------- #

# ARMOR SLAM
# Buffs the attacker's team defense by 20% for 3 seconds (300 ticks); 5s cooldown
def armor_slam_effect(attacker: Dino, defender: Dino, game_state: GameState, damage: float):
    if attacker.cooldown:
        return
    attacker_team = next(team for team in game_state.teams.values() if attacker in team)
    team_modifiers = {}
    for dino in attacker_team:
        flat_modifier = int(dino.stats.defense * 0.25)  # 20% of original defense
        team_modifiers[dino.id] = flat_modifier
        dino.stats.defense += flat_modifier
        game_state.log_effect("defense_buff", dino, "defense", flat_modifier)
    attacker.cooldown = True  

    def restore_defense():
        for dino in attacker_team:
            if dino.id in team_modifiers:
                dino.stats.defense -= team_modifiers[dino.id]
                game_state.log_effect("defense_debuff", dino, "defense", -team_modifiers[dino.id])

    def reset_cooldown():
        attacker.cooldown = False

    game_state.schedule_action(300, 2, restore_defense, "armor_slam", attacker.id, "restore_defense")
    game_state.schedule_action(500, 2, reset_cooldown, "armor_slam", attacker.id, "reset_cooldown")


# SPIKE TAIL SWEEP
# Reflects 30% of damage back to the attacker on next attack received
def spike_tail_sweep_effect(attacker: Dino, defender: Dino, game_state: GameState, damage: float):
    if "reflect" in attacker.current_statuses:
        return
    attacker.current_statuses.append("reflect")


# HORNED CHARGE
# Stuns the target for 1.5 seconds (150 ticks); 2s cooldown
def horned_charge_effect(attacker: Dino, defender: Dino, game_state: GameState, damage: float):
    if attacker.cooldown:
        return
    # reschedule the defender's next action to be 100 ticks later (remove existing action if any)
    new_queue = []
    for action in game_state.action_queue:
        # Keep all actions except the defender's next scheduled attack
        if not (action.action_type == "dino_action" and action.dino_id == defender.id):
            new_queue.append(action)

    # Replace the original queue with our filtered queue
    game_state.action_queue = new_queue
    heapq.heapify(game_state.action_queue)

    game_state.schedule_action(150, 1, lambda d=defender: game_state.dino_action(d), "dino_action", defender.id)  # Schedule the defender's next action after the stun duration
    
    game_state.log_effect("stun", defender, "stun", 150)  # Log the stun effect
    attacker.cooldown = True  
    
    def reset_cooldown():
        attacker.cooldown = False
    game_state.schedule_action(300, 2, reset_cooldown, "horned_charge", attacker.id, "reset_cooldown")


# CRUSHING BITE
# has a 30% chance to ignore the target's defense for this attack
def crushing_bite_before_effect(attacker: Dino, defender: Dino, game_state: GameState):
    if random.random() < 0.3:  # 30% chance to ignore defense
        damage, miss = game_state.dino_attack(attacker, defender, custom_stats=(None, None, 0, None, None))
        return False, miss  # Skip the normal attack
    return True, False  # Proceed with the normal attack


# RAPID SLASH
# Hits 2 to 5 times in a row, defense is applied at the end.
def rapid_slash_before_effect(attacker: Dino, defender: Dino, game_state: GameState):
    
    stats = [attacker.stats.atk, attacker.attack.dmg_multiplier, 0, attacker.stats.crit_chance, attacker.stats.crit_damage]
    
    # Apply individual abilities that modify attack parameters before damage calculation
    from Blog.utils.dw_pvm_abilities import apply_individual_abilities_before_attack
    attack_modifications = apply_individual_abilities_before_attack(attacker, defender, game_state)
    
    # Apply damage multiplier (Chasseur nocturne)
    damage_multiplier = attack_modifications.get('damage_multiplier', 1.0)
    
    # hit distribution : 45% 2 hits, 35% 3 hits, 15% 4 hits, 5% 5 hits
    hit_distribution = [2, 3, 4, 5]
    probabilities = [0.40, 0.35, 0.15, 0.10]
    hits = random.choices(hit_distribution, probabilities)[0]
    game_state.log_effect("rapid_slash", attacker, "hits", hits)  # Log the number of hits
    total_damage = 0
    crit_nb = 0
    for _ in range(hits):
        damage, is_crit = game_state.calculate_damage(*stats)
        total_damage += damage
        if is_crit:
            crit_nb += 1
    total_damage -= defender.stats.defense  # Apply defense at the end
    total_damage = max(0, total_damage)  # Ensure damage is not negative
    damage, miss = game_state.dino_attack(attacker, defender, None, total_damage, crit_nb>1)  # Apply the total damage to the defender
    return False, miss  # Skip the normal attack


# BLEEDING STRIKE
# Applies bleed for 3 seconds (300 ticks); 5s cooldown
# Bleed status increases damage taken by 10% 
def bleeding_strike_effect(attacker: Dino, defender: Dino, game_state: GameState, damage: float):
    if attacker.cooldown:
        return
    
    attacker.cooldown = True
    if "bleed" not in defender.current_statuses:
        defender.current_statuses.append("bleed")
        game_state.log_effect("bleed", defender, "bleed", 0.2)  # Log the bleed effect
    else:
        new_queue = []
        for action in game_state.action_queue:
            # Keep all actions except the one you want to remove
            if not (action.effect_name == "remove_bleed" and action.dino_id == defender.id):
                new_queue.append(action)
        # Replace the original queue with our filtered queue
        game_state.action_queue = new_queue
        heapq.heapify(game_state.action_queue)
                
    def remove_bleed():
        if "bleed" in defender.current_statuses:
            defender.current_statuses.remove("bleed")
            game_state.log_effect("bleed_remove", defender, "bleed", -0.2)

    def reset_cooldown():
        attacker.cooldown = False

    game_state.schedule_action(300, 2, remove_bleed, "bleeding_strike", defender.id, "remove_bleed")
    game_state.schedule_action(500, 2, reset_cooldown, "bleeding_strike", attacker.id, "reset_cooldown")
    

# ECHOING ROAR
# Buffs attacker's team speed by 15% for 3 seconds (300 ticks); 5s cooldown
def echoing_roar_effect(attacker: Dino, defender: Dino, game_state: GameState, damage: float):
    if attacker.cooldown:
        return
    
    attacker.cooldown = True
    attacker_team = next(team for team in game_state.teams.values() if attacker in team)
    team_modifiers = {}
    for dino in attacker_team:
        flat_modifier = round(dino.stats.speed * 0.2, 2)  # 20% of original speed
        team_modifiers[dino.id] = flat_modifier
        dino.stats.speed += flat_modifier
        game_state.log_effect("speed_buff", dino, "speed", flat_modifier)

    def restore_speed():
        for dino in attacker_team:
            if dino.id in team_modifiers:
                dino.stats.speed -= team_modifiers[dino.id]
                game_state.log_effect("speed_debuff", dino, "speed", -team_modifiers[dino.id])

    def reset_cooldown():
        attacker.cooldown = False

    cooldown = jungle_perfide_terrain(500, game_state, attacker)  # Adjust cooldown based on terrain
    game_state.schedule_action(300, 2, restore_speed, "echoing_roar", attacker.id, "restore_speed")
    game_state.schedule_action(cooldown, 2, reset_cooldown, "echoing_roar", attacker.id, "reset_cooldown")


# VENOM SPIT
# Inflicts poison for 3 seconds (300 ticks); 5s cooldown
# Poison status deals 4% of current HP as damage every half second (50 ticks)
def venom_spit_effect(attacker: Dino, defender: Dino, game_state: GameState, damage: float):
    if attacker.cooldown:
        return

    def poison_damage():
        if defender.is_alive() and "poison" in defender.current_statuses:
            damage = int(defender.current_hp * 0.04)
            defender.current_hp -= damage
            defender.current_hp = int(defender.current_hp)
            # Source is the attacker who applied poison initially
            game_state.log_effect("poison_damage", defender, "hp", damage, source=attacker)
            if defender.is_alive():
                game_state.schedule_action(50, 2, poison_damage, "venom_spit", defender.id, "poison_damage")
            else:
                # If the defender dies from poison, apply death effects
                game_state.apply_death_effects(defender)

    def remove_poison():
        if "poison" in defender.current_statuses:
            defender.current_statuses.remove("poison")
            game_state.log_effect("poison_remove", defender, "poison", -0.04)

    def reset_cooldown():
        attacker.cooldown = False
        
    attacker.cooldown = True
    if "poison" not in defender.current_statuses:
        defender.current_statuses.append("poison")
        game_state.log_effect("poison", defender, "poison", 0.04, source=attacker)  # Log the poison effect
        game_state.schedule_action(50, 2, poison_damage, "venom_spit", defender.id, "poison_damage") # Schedule the first poison damage
    else:
        new_queue = []
        for action in game_state.action_queue:
            # Keep all actions except the one you want to remove
            if not (action.effect_name == "remove_poison" and action.dino_id == defender.id):
                new_queue.append(action)
        # Replace the original queue with our filtered queue
        game_state.action_queue = new_queue
        heapq.heapify(game_state.action_queue)

    cooldown = jungle_perfide_terrain(450, game_state, attacker)  # Adjust cooldown based on terrain
    game_state.schedule_action(300, 2, remove_poison, "venom_spit", defender.id, "remove_poison")
    game_state.schedule_action(cooldown, 2, reset_cooldown, "venom_spit", attacker.id, "reset_cooldown")


# SKY DIVE
# Grants a 75% chance to dodge the next attack; 1,5s cooldown
def sky_dive_effect(attacker: Dino, defender: Dino, game_state: GameState, damage: float):
    if attacker.cooldown or "dodge" in attacker.current_statuses:
        return
    attacker.cooldown = True
    attacker.current_statuses.append("dodge")
    attacker.stats.dodge += 0.75  # Increase dodge chance by 75%
    game_state.log_effect("dodge_buff", attacker, "dodge", 0.75)  # Log the dodge effect

    def reset_cooldown():
        attacker.cooldown = False

    cooldown = jungle_perfide_terrain(150, game_state, attacker)  # Adjust cooldown based on terrain
    game_state.schedule_action(cooldown, 2, reset_cooldown, "sky_dive", attacker.id, "reset_cooldown")