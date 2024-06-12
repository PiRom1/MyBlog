from django import forms
from django.contrib.auth.models import User


class MessageForm(forms.Form):

    
    #CHOICES = [(user.name, user.name) for user in User.objects.all()]

    #who = forms.ChoiceField(label = 'Who', widget = forms.RadioSelect, choices = CHOICES)
    message = forms.CharField(label="Message", max_length=1000)


class LoginForm(forms.Form):
    users = User.objects.all()

    CHOICES = [(user.username, user.username) for user in User.objects.all()]

    username = forms.ChoiceField(label = 'username', choices = CHOICES)
    password = forms.CharField(label = 'password', widget = forms.PasswordInput, max_length = 100)