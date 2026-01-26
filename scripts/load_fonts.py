from Blog.models import Font
import pickle as pkl

def run():
    font_list = pkl.load(open("scripts/fonts.pkl", "rb"))
    for font in font_list:
        if 'Playwrite' not in font:
            Font.objects.get_or_create(name = font)
    
    Font.objects.create(name = "Playwrite FR Trad")