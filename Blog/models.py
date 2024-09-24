from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import datetime

# Create your models here.


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a user with the given email, logo and password.
        """
        user = self.model(
            email = self.normalize_email(email),
            **extra_fields
        )

        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user
        
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email, logo and password.
        """
        user = self.create_user(
            email,
            password=password,
            **extra_fields
        )

        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user


class Photo(models.Model):
    image = models.ImageField(upload_to = 'Images/')

    def __str__(self):
        return f"{(self.image)}".replace("Images/", "")
    

class User(AbstractUser):
    objects = UserManager()
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    image = models.ForeignKey(Photo, on_delete=models.CASCADE, null=True)
    
    
    class Meta:
        verbose_name = 'Utilisateur'

    def __str__(self):
        return f'{self.username}'

class Session(models.Model):
    session_name = models.TextField("name", default = "")

    def __str__(self):
        return f"{self.session_name}"

class SessionUser(models.Model):
    session = models.ForeignKey(Session, on_delete = models.CASCADE)
    user = models.ForeignKey(User, on_delete = models.CASCADE)

    def __str__(self):
        return f"{self.user} ({self.session})"


class Message(models.Model):

    pub_date = models.DateTimeField("Date publication")
    writer = models.ForeignKey(User, on_delete = models.CASCADE)
    text = models.TextField("Texte")
    upvote = models.IntegerField("upvote", default = 0)
    downvote = models.IntegerField("downvote", default = 0)
    color = models.CharField("color", max_length = 50, default = "")
    session_id = models.ForeignKey(Session, on_delete = models.CASCADE)

    def __str__(self):
        return f"{self.writer} ({self.pub_date}) : {self.text}"

class History(models.Model):

    pub_date = models.DateTimeField("Date modification")
    writer = models.ForeignKey(User, on_delete = models.CASCADE)
    text = models.TextField("Texte")
    message = models.ForeignKey(Message, on_delete = models.CASCADE)


class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]

    CATEGORIES = [
        ('undefined', 'Undefined'),
        ('feature', 'Feature'),
        ('fix', 'Fix')
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, related_name='assigned_tickets', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    category = models.CharField(max_length=20, choices = CATEGORIES, default = 'undefined')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title



# Models for sondage. Une question, des choix associés, chaque user peut choisir un choix
class Sondage(models.Model):
    question = models.TextField()
    pub_date = models.DateField("Date publication", default = datetime.date.today)
    current = models.BooleanField(default = False)

    def __str__(self):
        return self.question
    

class SondageChoice(models.Model):
    choice = models.TextField(blank = True)
    sondage = models.ForeignKey(Sondage, on_delete = models.CASCADE)
    votes = models.IntegerField(default = 0)

    def __str__(self):
        return self.choice


class ChoiceUser(models.Model):
    choice = models.ForeignKey(SondageChoice, on_delete = models.CASCADE)
    user = models.ForeignKey(User, on_delete = models.CASCADE)


class Recit(models.Model): # Texte en mode cadavre exquis
    name = models.CharField(default = None, max_length = 100)

    def __str__(self):
        return self.name

class Texte(models.Model): # Texte composant un récit
    text = models.TextField("Texte")
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    recit = models.ForeignKey(Recit, on_delete = models.CASCADE)

    def __str__(self):
        return(f"{self.user} : {self.text}")

