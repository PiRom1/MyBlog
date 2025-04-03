from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_icon_class(slot_type):
    icon_mapping = {
        'hp': 'heart',
        'atk': 'sword-alt',
        'defense': 'shield',
        'spd': 'bolt',
        'crit': 'location-crosshairs',
        'crit_dmg': 'burst'
    }
    return icon_mapping.get(slot_type, 'circle-question')

@register.filter
def get_rarity_class(rarity):
    rarity_mapping = {
        'common': 'fi-cyan',
        'uncommon': 'fi-blue',
        'rare': 'fi-purple',
        'legendary': 'fi-red'
    }
    return rarity_mapping.get(rarity, 'fi-gray')

@register.filter
def split_string(value, delimiter=','):
    return value.split(delimiter)