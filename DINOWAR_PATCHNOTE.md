# DinoWar - Patchnote

DinoWar is an advanced battle system featuring dinosaurs with unique attacks and abilities. The system includes both regular DinoWars battles and an advanced PVM (Player vs Monster) roguelike mode with enhanced ability mechanics.

This is the patchnote of dinowar, indicating the latest changes to the game.

Changes are described by a "before" and "after" lines for each abilities.

## Table of Contents

1. [Regular DinoWars Abilities](#regular-dinowars-abilities)
2. [PVM Mode Abilities](#pvm-mode-abilities)

---

## Regular DinoWars Abilities

These abilities are used in standard DinoWars battles between players.

### Single Dino Abilities

These abilities affect only the attacking dinosaur or its direct target.

#### NO CHANGES

### All Team Abilities

#### NO CHANGES

---

## PVM Mode Abilities

These advanced abilities are available in the PVM (Player vs Monster) roguelike mode, offering more complex strategic gameplay.

### Single Dino Abilities

#### **Boost de vie**
- **Before**: At the start of the battle, increases this dino's HP by 20%
- **No changes**

#### **Boost d'attaque**
- **Before**: At the start of the battle, increases this dino's ATK by 20%
- **No changes**

#### **Boost de défense**
- **Before**: At the start of the battle, increases this dino's DEF by 20%
- **No changes**

#### **Boost de vitesse**
- **Before**: At the start of the battle, increases this dino's SPD by 0.2
- **After**: At the start of the battle, increases this dino's SPD by 20%

#### **Boost de % critique**
- **Before**: At the start of the battle, increases this dino's critical chance by 0.08
- **After**: At the start of the battle, increases this dino's critical chance by 0.1

#### **Boost de dégâts critiques**
- **Before**: At the start of the battle, increases this dino's critical damage by 0.2
- **After**: At the start of the battle, increases this dino's critical damage by 30%

#### **Frénésie**
- **Before**: +20% attack speed when HP drops below 30%
- **After**: +25% attack speed when HP drops below 50%

#### **Bourreau**
- **Before**: After attacking, if target's remaining HP is lower than the damage dealt, the target dies instantly
- **After**: When attacking, the more target's remaining HP is low, the more chances this dino have to kill the target instantly ((1-(remaining HP/total HP)^2)/1.1)

#### **Peau dure**
- **Before**: 15% damage reduction when HP is above 70%
- **After**: 20% damage reduction when HP is above 50%

#### **Inspiration héroïque**
- **Before**: When this dino lands a critical hit, all allies gain +20% ATK for 1 second
- **After**: When this dino lands a critical hit, all allies gain +25% ATK for 1 second

#### **Vol de vie**
- **Before**: Heals attacker for 15% of damage dealt after each attack
- **After**: Heals attacker for 30% of damage dealt after each attack

#### **Provocation**
- **Before**: This dino is 2x more likely to be targeted by enemies
- **No changes**

#### **Agilitée accrue**
- **Before**: When this dino is attacked, it has 20% chance to dodge the attack
- **No changes**

#### **Regard pétrifiant**
- **Before**: 25% chance on attack to reduce target's speed by 50% for 3 seconds
- **After**: After attacking, reduce target's speed by 25% for 3 seconds

#### **Régénération**
- **Before**: Every 2 seconds, heals for 5% of maximum HP
- **No changes**

#### **Chasseur nocturne**
- **Before**: Gains +30% critical chance against enemies afflicted with status effects (poison & bleed)
- **After**: Deals 2x damage against enemies afflicted with status effects (poison & bleed)

#### **Carapace robuste**
- **Before**: Starts each fight at 90% damage resistance. Damage resistance drops by 20% each time this dino takes damage (can go negative, meaning extra damage taken)
- **After**: Starts each fight at 50% damage reduction. Damage reduction drops by 3% each time this dino takes damage (can go negative down to -25%)

### All Team Abilities

#### **Dernier souffle**
- **Before**: When an ally dies, all other living allies immediately recover 20% HP
- **No changes**

#### **Sprint préhistorique**
- **Before**: +15% speed to whole team for the first 5 seconds of battle
- **After**: +20% speed to whole team for the first 5 seconds of battle

#### **Esprit de meute**
- **Before**: +20% ATK if all allies are alive, -10% ATK otherwise
- **No changes**

#### **Bouclier collectif**
- **Before**: 20% of damage received is shared equally among all living allies
- **After**: 50% of damage received is shared equally among all other living allies

#### **Instinct protecteur**
- **Before**: When any team member takes a critical hit, the whole team gains +20% DEF for 1 second
- **After**: When any team member takes a critical hit, the whole team gains +30% DEF for 2 seconds

#### **Pression croissante**
- **Before**: Every 3 seconds, the team's ATK increases by +5% (stacks throughout battle)
- **No changes**

#### **Seul contre tous**
- **Before**: When only one dino remains alive, it gains +20% DEF
- **After**: When only one dino remains alive, it gains +25% in all stats

#### **Terreur collective**
- **Before**: When an enemy dies, the whole team gains +8% ATK permanently until end of battle
- **After**: When an enemy dies, the whole team gains +15% ATK permanently until end of battle

#### **Mort-vivant**
- **Before**: When this dino dies, it continues attacking for 2 seconds without being targetable (unless it's the last dino alive)
- **After**: This is now a team ability. When **the first** dino dies, it continues attacking for 2 seconds without being targetable