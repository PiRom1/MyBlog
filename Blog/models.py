from django.db import models
from django.contrib.auth.models import User, AbstractUser

# Create your models here.
class Session(models.Model):
    session_name = models.TextField("name", default = "")
    session_id = models.IntegerField(default = 0)


class Message(models.Model):

    pub_date = models.DateTimeField("Date publication")
    writer = models.ForeignKey(User, on_delete = models.CASCADE)
    text = models.TextField("Texte")
    upvote = models.IntegerField("upvote", default = 0)
    downvote = models.IntegerField("downvote", default = 0)
    color = models.CharField("color", max_length = 50, default = "")
    session_id = models.IntegerField("session_id", default = 0)

    def __str__(self):
        return f"{self.writer} ({self.pub_date}) : {self.text}"

    

class History(models.Model):

    pub_date = models.DateTimeField("Date modification")
    writer = models.ForeignKey(User, on_delete = models.CASCADE)
    text = models.TextField("Texte")
    message = models.ForeignKey(Message, on_delete = models.CASCADE)