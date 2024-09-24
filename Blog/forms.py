from django import forms
from django.forms import modelformset_factory
from .models import *



class ModifyForm(forms.Form):
    modify = forms.CharField(label = "Modify")


class ModifyUserForm(forms.Form):
    first_name = forms.CharField(label = "Prénom", required = False)
    last_name = forms.CharField(label = "Nom", required = False)
    email = forms.EmailField(label = "Mail", required = False)


class CharForm(forms.Form):
    message = forms.CharField(label="Message")    


class MessageForm(forms.Form):
   

    CHOICES = [('black', 'Noir'), ('red', 'Rouge'), ('blue', 'Bleu'), ('green', 'Vert'), ('yellow', 'Jaune'), ('pink', 'Rose'), ('purple', 'Violet')]

    color = forms.ChoiceField(label = 'Ta couleur', choices = CHOICES)

    message = forms.CharField(label="Message",
                              widget=forms.Textarea(attrs={'rows': 5, 'cols': 100})) 



class MessageForm2(forms.Form):
   

    message = forms.CharField(label="Message",
                              widget=forms.Textarea(attrs={'rows': 5, 'cols': 100})) 


class LoginForm(forms.Form):
    try:
        CHOICES = [(user.username, user.username) for user in User.objects.all()]
    except Exception as e:
        CHOICES = []

    username = forms.CharField(label = 'username', max_length = 100)
    password = forms.CharField(label = 'password', widget = forms.PasswordInput, max_length = 100)


class AddUserForm(forms.Form):
    
    username = forms.CharField(label = 'username', max_length = 100)
    password = forms.CharField(label = 'password', widget = forms.PasswordInput, max_length = 100)


class ColorForm(forms.Form):
    
    CHOICES = [('red', 'red'), ('blue', 'blue'), ('green', 'green')]

    user_color = forms.ChoiceField(label = 'Ta couleur', choices = CHOICES)

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'category', 'description', 'assigned_to', 'status']


class SondageForm(forms.ModelForm):
    class Meta:
        model = Sondage
        fields = ['question', 'current']

    
    
class ChoiceForm(forms.ModelForm):
    class Meta:
        model = SondageChoice
        fields = ['choice']
        
        widgets = {
            'choice': forms.TextInput(attrs={
            'style': 'width: 300px; height: 40px;',  # Vous pouvez ajuster ces valeurs selon vos besoins
            }),
        }

from django.forms import formset_factory
from django.forms import modelformset_factory

# Créer un formset pour les choix du sondage
ChoiceFormSet = formset_factory(ChoiceForm, extra=5)
ChoiceFormSet0 = modelformset_factory(SondageChoice, ChoiceForm, extra=0)





class PhotoForm(forms.Form):
    photo = forms.ImageField(label = "Choisissez votre photo de profil")
