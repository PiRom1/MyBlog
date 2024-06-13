from django import forms
from django.contrib.auth.models import User


class MessageForm(forms.Form):

    
    #CHOICES = [(user.name, user.name) for user in User.objects.all()]

    #who = forms.ChoiceField(label = 'Who', widget = forms.RadioSelect, choices = CHOICES)

    CHOICES = [('black', 'Noir'), ('red', 'Rouge'), ('blue', 'Bleu'), ('green', 'Vert'), ('yellow', 'Jaune')]

    color = forms.ChoiceField(label = 'Ta couleur', choices = CHOICES)

    message = forms.CharField(label="Message",
                              widget=forms.TextInput(attrs={'size':100}))


class LoginForm(forms.Form):

    CHOICES = [(user.username, user.username) for user in User.objects.all()]

    username = forms.ChoiceField(label = 'username', choices = CHOICES)
    password = forms.CharField(label = 'password', widget = forms.PasswordInput, max_length = 100)


class AddUserForm(forms.Form):
    
    username = forms.CharField(label = 'username', max_length = 100)
    password = forms.CharField(label = 'password', widget = forms.PasswordInput, max_length = 100)


class ColorForm(forms.Form):
    
    CHOICES = [('red', 'red'), ('blue', 'blue'), ('green', 'green')]

    user_color = forms.ChoiceField(label = 'Ta couleur', choices = CHOICES)
    