from django import template

register = template.Library()

@register.inclusion_tag('Blog/jeux/leaderboard_table.html')
def render_leaderboard(scores):
    return {'scores': scores}
