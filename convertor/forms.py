from django import forms
from .models import *

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['file']
    
        widgets = {

                'file': forms.ClearableFileInput(attrs={'allow_multiple_selected': True})

            }


class FolderForm(forms.Form):
    path = forms.FilePathField(path = "/", allow_files = False, allow_folders = True)


class PhotoSetForm(forms.ModelForm):
    class Meta:
        model = PhotoSet
        fields = ['text']

class PhotoFileForm(forms.ModelForm):
    class Meta:
        model = PhotoFile
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'allow_multiple_selected': True}),
        }
        # widget is important to upload multiple files