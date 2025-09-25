# DinoWar - Complete Abilities Guide

DinoWar is an advanced battle system featuring dinosaurs with unique attacks and abilities. The system includes both regular DinoWars battles and an advanced PVM (Player vs Monster) roguelike mode with enhanced ability mechanics.

## Table of Contents

1. [Regular DinoWars Abilities](#regular-dinowars-abilities)
2. [PVM Mode Abilities](#pvm-mode-abilities)

---

## Regular DinoWars Abilities

These abilities are used in standard DinoWars battles between players.

### Single Dino Abilities

These abilities affect only the attacking dinosaur or its direct target.

#### **Spike Tail Sweep**
- **Effect**: Reflects 30% of damage back to the attacker on next attack received
- **Cooldown**: None (single use)

#### **Horned Charge**
- **Effect**: Stuns the target for 1.5 seconds (150 ticks)
- **Cooldown**: 2 seconds

#### **Crushing Bite**
- **Effect**: 30% chance to ignore the target's defense for this attack
- **Cooldown**: None

#### **Rapid Slash**
- **Effect**: Hits 2-5 times in a row (40% for 2 hits, 35% for 3 hits, 15% for 4 hits, 10% for 5 hits), defense is applied at the end
- **Cooldown**: None

#### **Bleeding Strike**
- **Effect**: Applies bleed status for 3 seconds (causes target to take 10% extra damage)
- **Cooldown**: 5 seconds
- **Duration**: 3 seconds

#### **Venom Spit**
- **Effect**: Inflicts poison for 3 seconds (deals 4% of current HP as damage every 0.5 seconds)
- **Cooldown**: 5 seconds
- **Duration**: 3 seconds

#### **Sky Dive**
- **Effect**: Grants 75% chance to dodge the next attack
- **Cooldown**: 1.5 seconds

### All Team Abilities

These abilities affect the entire team of the ability user.

#### **Armor Slam**
- **Effect**: Buffs the attacker's entire team defense by 20% for 3 seconds
- **Cooldown**: 5 seconds
- **Duration**: 3 seconds

#### **Echoing Roar**
- **Effect**: Buffs the attacker's entire team speed by 15% for 3 seconds
- **Cooldown**: 5 seconds
- **Duration**: 3 seconds

---

## PVM Mode Abilities

These advanced abilities are available in the PVM (Player vs Monster) roguelike mode, offering more complex strategic gameplay.

### Single Dino Abilities

#### **Boost de vie**
- **Effect**: At the start of the battle, increases this dino's HP by 20%

#### **Boost d'attaque**
- **Effect**: At the start of the battle, increases this dino's ATK by 20%

#### **Boost de défense**
- **Effect**: At the start of the battle, increases this dino's DEF by 20%

#### **Boost de vitesse**
- **Effect**: At the start of the battle, increases this dino's SPD by 0.2

#### **Boost de % critique**
- **Effect**: At the start of the battle, increases this dino's critical chance by 0.08

#### **Boost de dégâts critiques**
- **Effect**: At the start of the battle, increases this dino's critical damage by 0.2

#### **Mort-vivant**
- **Effect**: When this dino dies, it continues attacking for 2 seconds without being targetable (unless it's the last dino alive)

#### **Frénésie**
- **Effect**: +20% attack speed when HP drops below 30%

#### **Boureau**
- **Effect**: After attacking, if target's remaining HP is lower than the damage dealt, the target dies instantly

#### **Peau dure**
- **Effect**: 15% damage reduction when HP is above 70%

#### **Inspiration héroïque**
- **Effect**: When this dino lands a critical hit, all allies gain +20% ATK for 1 second

#### **Vol de vie**
- **Effect**: Heals attacker for 15% of damage dealt after each attack

#### **Provocation**
- **Effect**: This dino is 2x more likely to be targeted by enemies

#### **Agilitée accrue** 
- **Effect**: When this dino is attacked, it has 20% chance to dodge the attack

#### **Regard pétrifiant** 
- **Effect**: 25% chance on attack to reduce target's speed by 50% for 3 seconds

#### **Régénération** 
- **Effect**: Every 2 seconds, heals for 5% of maximum HP

#### **Chasseur nocturne** 
- **Effect**: Gains +30% critical chance against enemies afflicted with status effects (poison & bleed)

#### **Carapace robuste** 
- **Effect**: Starts each fight at 90% damage resistance. Damage resistance drops by 20% each time this dino takes damage (can go negative, meaning extra damage taken)

### All Team Abilities

#### **Dernier souffle**
- **Effect**: When an ally dies, all other living allies immediately recover 20% HP

#### **Sprint préhistorique**
- **Effect**: +15% speed to whole team for the first 5 seconds of battle

#### **Esprit de meute**
- **Effect**: +20% ATK if all allies are alive, -10% ATK otherwise

#### **Bouclier collectif**
- **Effect**: 20% of damage received is shared equally among all living allies

#### **Instinct protecteur**
- **Effect**: When any team member takes a critical hit, the whole team gains +20% DEF for 1 second

#### **Pression croissante**
- **Effect**: Every 3 seconds, the team's ATK increases by +5% (stacks throughout battle)

#### **Seul contre tous**
- **Effect**: When only one dino remains alive, it gains +20% DEF

#### **Terreur collective**
- **Effect**: When an enemy dies, the whole team gains +8% ATK permanently until end of battle

## Design Philosophy

### Balance Considerations

**Single Dino Abilities** focus on:
- Individual tactical decisions
- Risk/reward mechanics
- Specialized roles and counters
- Timing-based gameplay

**All Team Abilities** focus on:
- Strategic team building
- Coordination rewards
- Meta-game considerations
- Long-term battle dynamics

### Power Level Guidelines

- **Immediate effects**: Higher impact but shorter duration
- **Conditional effects**: Higher power when conditions are met
- **Permanent effects**: Lower individual impact but cumulative value
- **Cooldown abilities**: Higher power balanced by availability windows


