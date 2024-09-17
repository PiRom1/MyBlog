from django import template
import re

register = template.Library()

@register.filter(name='highlight')
def highlight_tag(value, tag):
    """Entoure le mot 'tag' dans le texte avec une balise <strong> pour le mettre en gras"""
    if tag:
        # Utilisation des expressions régulières pour mettre en gras le mot
        return re.sub(f'({re.escape(tag)})', r'<strong>\1</strong>', value, flags=re.IGNORECASE)
    return value