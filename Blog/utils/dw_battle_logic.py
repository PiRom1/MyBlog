import json
import heapq
import random
from dataclasses import dataclass, field, asdict
from typing import Callable, List, Dict
from django.db.models import Model


@dataclass
class DinoStats:
    hp: float
    atk: float
    defense: float
    speed: float  # attacks per second
    crit_chance: float
    crit_damage: float


@dataclass
class Attack:
    name: str
    dmg_multiplier: tuple  # (min, max)
    on_hit_effect: Callable[['Dino', 'Dino', 'GameState'], None] = None


@dataclass
class Dino:
    id: int
    name: str
    user: str
    stats: DinoStats
    attack: Attack
    current_hp: float = field(init=False)
    current_statuses: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.current_hp = self.stats.hp

    def is_alive(self):
        return self.current_hp > 0


@dataclass(order=True)
class ScheduledAction:
    tick: int
    priority: int
    action: Callable[[], None] = field(compare=False)


class GameState:
    def __init__(self, team1: tuple[str, List[Dino]], team2: tuple[str, List[Dino]]):
        self.teams = {team1[0]: team1[1], team2[0]: team2[1]}
        self.tick = 0
        self.action_queue: List[ScheduledAction] = []
        self.fight_log: List[Dict] = []
        self.log_initial_state()

    def log_initial_state(self):
        initial_state = {
            "tick": 0,
            "initial_state": {
                team_name: [asdict(dino) for dino in dinos]
                for team_name, dinos in self.teams.items()
            }
        }
        self.fight_log.append(initial_state)

    def schedule_action(self, tick_delay: int, priority: int, action: Callable[[], None]):
        heapq.heappush(self.action_queue, ScheduledAction(self.tick + tick_delay, priority, action))

    def run(self):
        # Schedule initial attacks for all dinos
        for team_name, dinos in self.teams.items():
            for dino in dinos:
                interval = int(100 / dino.stats.speed)
                self.schedule_action(interval, 1, lambda d=dino: self.dino_attack(d))

        while self.action_queue and all(any(d.is_alive() for d in team) for team in self.teams.values()):
            next_tick = self.action_queue[0].tick
            self.tick = next_tick

            actions_this_tick = []
            while self.action_queue and self.action_queue[0].tick == next_tick:
                actions_this_tick.append(heapq.heappop(self.action_queue))

            for action in actions_this_tick:
                action.action()

        # Log final state, export fight log, and return results
        final_state = {
            "tick": self.tick,
            "final_state": {
                team_name: [asdict(dino) for dino in dinos]
                for team_name, dinos in self.teams.items()
            },
            "winner": self.get_winner(),
        }
        self.fight_log.append(final_state)
        return json.dumps(self.fight_log, indent=2)

    def dino_attack(self, attacker: Dino, target: Dino = None):
        if not attacker.is_alive():
            return

        if target:
            defender = target
        else:
            defender = self.choose_target(attacker)

        if defender:
            damage, is_crit = self.calculate_damage(attacker, defender)
            defender.current_hp -= damage

            log_entry = {
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

            # Apply on-hit effect if any
            if attacker.attack.on_hit_effect:
                attacker.attack.on_hit_effect(attacker, defender, self)

        # Schedule next attack
        interval = int(100 / attacker.stats.speed)
        self.schedule_action(interval, 1, lambda d=attacker: self.dino_attack(d))

    def choose_target(self, attacker: Dino):
        enemy_team = next(team for team in self.teams.values() if attacker not in team)
        opponents = [d for d in enemy_team if d.is_alive()]
        return random.choice(opponents) if opponents else None

    def calculate_damage(self, attacker: Dino, defender: Dino):
        atk_stats = attacker.stats
        multiplier = random.uniform(*attacker.attack.dmg_multiplier)
        base_dmg = atk_stats.atk * multiplier

        is_crit = random.random() < atk_stats.crit_chance
        if is_crit:
            base_dmg *= atk_stats.crit_damage

        damage_after_def = base_dmg - defender.stats.defense
        return max(0, damage_after_def), is_crit
    
    def log_effect(self, event: str, dino: Dino, stat: str, value: float):
        log_entry = {
            "tick": self.tick,
            "event": event, # event name or description
            "dino": dino.name, # dino affected
            "dino_id": dino.id,
            "stat": stat, # stat affected (e.g., "defense", "speed")
            "value": value, # modifier value (e.g., -20 for debuff, +20 for buff)
            "new_value": getattr(dino.stats, stat) # new value after applying the effect
        }
        self.fight_log.append(log_entry)

    def get_winner(self):
        for team_name, dinos in self.teams.items():
            if all(not dino.is_alive() for dino in dinos):
                return next(team for team in self.teams if team != team_name)
        return None
    
# Example of loading from Django models
def load_dino_from_model(userDino: Model, stats: Dict[str, float]) -> Dino:
    return Dino(
        id=userDino.id,
        name=str(userDino.dino),
        user=str(userDino.user),
        stats=DinoStats(
            hp=stats['hp'],
            atk=stats['atk'],
            defense=stats['defense'],
            speed=stats['spd'],
            crit_chance=stats['crit'],
            crit_damage=stats['crit_dmg']
        ),
        attack=Attack(
            name=userDino.attack.name,
            dmg_multiplier=(userDino.attack.min_dmg, userDino.attack.max_dmg),
            # On-hit effect is the name of the attack, concatenated with "_effect"
            on_hit_effect=globals().get(f"{userDino.attack.name}_effect", None)
        )
    )


# ------------------------- ATTACK EFFECTS ------------------------- #

# Example of an attack effect (debuff for 5 seconds)
def defense_debuff_effect(attacker: Dino, defender: Dino, game_state: GameState):
    original_defense = defender.stats.defense
    defender.stats.defense = max(0, defender.stats.defense - 20)

    def restore_defense():
        defender.stats.defense = original_defense

    # Debuff lasts for 500 ticks (5 seconds)
    game_state.schedule_action(500, 2, restore_defense)
