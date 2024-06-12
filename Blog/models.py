from django.db import models
from django.contrib.auth.models import User

# Create your models here.

 
# class User(models.Model):

#     #id = models.AutoField("id")
#     name = models.CharField("username", max_length = 50)
#     nickname = models.CharField("nickname", max_length = 50, default = "")



class Message(models.Model):

    pub_date = models.DateTimeField("Date publication")
    writer = models.ForeignKey(User, on_delete = models.CASCADE)
    text = models.TextField("Texte")
    upvote = models.IntegerField("upvote", default = 0)
    downvote = models.IntegerField("downvote", default = 0)

