from Blog.models import Font
import pickle as pkl

def run():
    font_list = pkl.load(open("scripts/fonts.pkl", "rb"))
    for font in font_list:
        Font.objects.create(name = font)