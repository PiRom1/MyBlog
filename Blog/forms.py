from django import forms
from .models import *



class ModifyForm(forms.Form):
    modify = forms.CharField(label = "Modify")


class ModifyUserForm(forms.Form):
    first_name = forms.CharField(label = "Prénom", required = False)
    last_name = forms.CharField(label = "Nom", required = False)
    email = forms.EmailField(label = "Mail", required = False)

    

class MessageForm(forms.Form):

    
    #CHOICES = [(user.name, user.name) for user in User.objects.all()]

    #who = forms.ChoiceField(label = 'Who', widget = forms.RadioSelect, choices = CHOICES)

    CHOICES = [('black', 'Noir'), ('red', 'Rouge'), ('blue', 'Bleu'), ('green', 'Vert'), ('yellow', 'Jaune'), ('pink', 'Rose'), ('purple', 'Violet')]

    color = forms.ChoiceField(label = 'Ta couleur', choices = CHOICES)

    message = forms.CharField(label="Message",
                              widget=forms.TextInput(attrs={'size':100}))


class LoginForm(forms.Form):

    CHOICES = [(user.username, user.username) for user in User.objects.all()]

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


class PhotoForm(forms.Form):
    photo = forms.ImageField(label = "Choisissez votre photo de profil")
