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