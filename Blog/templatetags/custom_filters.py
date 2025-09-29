from django import template
import re

register = template.Library()

@register.filter(name='highlight')
def highlight_tag(value, tag):
    """Entoure le mot 'tag' dans le texte avec une balise <strong> pour le mettre en gras"""
    replacements = [
    ('é', 'e'),
    ('è', 'e'),
    ('ê', 'e'),
    ('ë', 'e'),
    ('à', 'a'),
    ('â', 'a'),
    ('ä', 'a'),
    ('ù', 'u'),
    ('û', 'u'),
    ('ü', 'u'),
    ('î', 'i'),
    ('ï', 'i'),
    ('ô', 'o'),
    ('ö', 'o'),
    ('ç', 'c'),
    ('É', 'E'),
    ('È', 'E'),
    ('Ê', 'E'),
    ('Ë', 'E'),
    ('À', 'A'),
    ('Â', 'A'),
    ('Ä', 'A'),
    ('Ù', 'U'),
    ('Û', 'U'),
    ('Ü', 'U'),
    ('Î', 'I'),
    ('Ï', 'I'),
    ('Ô', 'O'),
    ('Ö', 'O'),
    ('Ç', 'C')
]

    for replacement in replacements:
        value = value.replace(replacement[0], replacement[1])

    if tag:
        # Utilisation des expressions régulières pour mettre en gras le mot
        return re.sub(f'({re.escape(tag)})', r'<strong>\1</strong>', value, flags=re.IGNORECASE)
    return value



@register.filter(name='index')
def index(indexable, i):
    return indexable[i]


@register.filter(name='effect_description')
def effect_description(event_name):
    """Convert PvM ability event names to user-friendly descriptions"""
    descriptions = {
        # Healing effects
        'dernier_souffle_heal': 'healed by Dernier souffle',
        'vol_de_vie': 'healed by Vol de vie',
        'regeneration': 'healed by Régénération',
        
        # Damage effects
        'poison_damage': 'damaged by poison',
        'reflect_damage': 'damaged by reflection',
        'bourreau_execute': 'executed by Bourreau',
        'bouclier_collectif_share': 'damage shared by Bouclier collectif',
        
        # Stat buffs/debuffs
        'sprint_prehistorique_buff': 'speed boosted by Sprint préhistorique',
        'sprint_prehistorique_debuff': 'speed boost expired',
        'frenesie_start': 'speed boosted by Frénésie',
        'frenesie_end': 'Frénésie effect ended',
        'inspiration_heroique_buff': 'attack boosted by Inspiration héroïque',
        'inspiration_heroique_debuff': 'attack boost expired',
        'esprit_de_meute': 'attack modified by Esprit de meute',
        'instinct_protecteur_buff': 'defense boosted by Instinct protecteur',
        'instinct_protecteur_debuff': 'defense boost expired',
        'pression_croissante': 'attack boosted by Pression croissante',
        'seul_contre_tous': 'defense boosted by Seul contre tous',
        'seul_contre_tous_remove': 'Seul contre tous effect removed',
        'terreur_collective': 'attack boosted by Terreur collective',
        'regard_petrifiant': 'speed reduced by Regard pétrifiant',
        'regard_petrifiant_restore': 'speed restored from Regard pétrifiant',
        
        # Special abilities
        'mort_vivant_start': 'became undead with Mort-vivant',
        'mort_vivant_end': 'Mort-vivant effect ended',
        'agilite_accrue_dodge': 'dodged with Agilitée accrue',
        'peau_dure': 'damage reduced by Peau dure',
        'bouclier_collectif_reduce': 'damage reduced by Bouclier collectif',
        'chasseur_nocturne': 'crit chance boosted by Chasseur nocturne',
        'carapace_robuste_start': 'damage resistance from Carapace robuste',
        'carapace_robuste_block': 'damage blocked by Carapace robuste',
        'carapace_robuste_amplify': 'extra damage from Carapace robuste',
        'carapace_robuste_degrade': 'Carapace robuste resistance degraded',
        
        # Basic effects
        'defense_buff': 'defense increased',
        'defense_debuff': 'defense decreased',
        'speed_buff': 'speed increased', 
        'speed_debuff': 'speed decreased',
        'bleed': 'bleeding started',
        'bleed_remove': 'bleeding ended',
        'poison': 'poisoned',
        'poison_remove': 'poison ended',
        'stun': 'stunned',
        'dodge': 'dodge attempt',
        'lac_putrefie': 'damaged by Lac putréfié terrain',
        
        # Special attack effects
        'rapid_slash': 'multiple hits from Rapid slash',
    }
    
    return descriptions.get(event_name, event_name.replace('_', ' ').title())


@register.filter(name='format_ticks')
def format_ticks(ticks):
    """Format a tick count into a readable string like "12s 34 ticks".
    Assumes 100 ticks = 1 second.
    Examples:
    - 0   -> "0 ticks"
    - 75  -> "75 ticks"
    - 100 -> "1s"
    - 134 -> "1s 34 ticks"
    """
    try:
        t = int(float(ticks))
    except (TypeError, ValueError):
        return ""

    seconds = t // 100
    remainder = t % 100

    parts = []
    if seconds > 0:
        parts.append(f"{seconds}s")
    if remainder > 0 or seconds == 0:
        parts.append(f"{remainder}")
    if seconds == 0:
        parts.append("ticks")
    return " ".join(parts)