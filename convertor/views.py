from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.conf import settings

from .forms import *
# Create your views here.
import os
from PIL import Image


def convert_to_png(image):
    
    cr2 = Image.open(os.path.join('media', str(image.file)))
    
    return cr2



def import_photos(request):

    form = PhotoForm(request.POST, request.FILES)
    
    if request.method == "POST":
        
        print(form.is_valid())

        if form.is_valid():
            name = form.cleaned_data['file']
            print("name : ",name)

            extension = str(name).split('.')[-1]

            if extension.lower() == 'cr2':
                
                form.save()
                return HttpResponseRedirect("convert")
    
    form = PhotoForm()

    context = {"form" : form}

    url = "convertor/import_photos.html"

    return render(request, url, context)



def import_photos_2(request):

    user = request.user
    is_valid = False
    if request.method == "POST":
        files = request.FILES.getlist('files')
        print(files)
        if files:
        
            for file in files:
                print(file.name.split('.')[-1].lower())
                if file.name.split('.')[-1].lower() == 'cr2':
                    
                    is_valid = True
                    file_path = os.path.join('MyBlog/media/Images/cr2', file.name)
                    print("liste : ", os.listdir('MyBlog/media'))
                    # Sauvegarder le fichier en utilisant les chunks (utile pour les gros fichiers)
                    with open(file_path, 'wb+') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
            print(is_valid)
            if is_valid:
                return HttpResponseRedirect('convert_2')
        
        

   
    

    context = {}
    return render(request, 'convertor/import_photos_2.html', context)







def convert(request):
    
    images = list(Photo.objects.filter(new=True))
    print("file 0 : ", images[0].file)
    for image in images:
        print('image : ', image)
        png = convert_to_png(image)

        name = str(image.file).split('/')[-1]
        name = name[:-3] + 'png'
        
        new_path = os.path.join("media", str(image.file).split("/")[0], "png", name)
        print(new_path)
        png.save(new_path)
        image.delete()
        del(png)
        os.remove(os.path.join("media", str(image.file)))
        

    return HttpResponseRedirect('/download')

progress = 0
def convert_2(request):
    CR2_PATH = 'MyBlog/media/Images/cr2'
    PNG_PATH = 'MyBlog/media/Images/png'

    images = os.listdir(CR2_PATH)
    
    for i,image in enumerate(images):
        
        cr2 = Image.open(os.path.join(CR2_PATH, image))
        

        
        new_image = image[:-3] + 'png'
        
        new_path = os.path.join(PNG_PATH, new_image)

        print(new_path)
        cr2.save(new_path)
        
        del(cr2)
        os.remove(os.path.join(CR2_PATH, image))

        progress = int(i+1 * 100 / len(images))
        print(progress)
        
    
    return HttpResponseRedirect('download')

import os
import zipfile
from django.http import HttpResponse
from django.conf import settings
from io import BytesIO

def download_zip(request):
    # Chemin vers le dossier contenant les fichiers que tu veux zipper
    folder_path = 'MyBlog/media/Images/png'
    print("download")
    # Crée un fichier en mémoire
    zip_buffer = BytesIO()

    # Création de l'archive ZIP
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                # Chemin absolu du fichier
                file_path = os.path.join(root, file)
                # Chemin relatif à partir du dossier compressé pour garder l'arborescence
                relative_path = os.path.relpath(file_path, folder_path)
                # Ajout du fichier au ZIP
                zip_file.write(file_path, relative_path)

    # Positionner le pointeur au début du fichier
    zip_buffer.seek(0)

    # Préparer la réponse HTTP pour télécharger le fichier ZIP
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=fichiers_compresses.zip'

    for file in os.listdir(folder_path):
        os.remove(os.path.join(folder_path, file))


    return response

    
