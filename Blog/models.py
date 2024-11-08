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
    yoda_counter = models.IntegerField("Yoda_counter", default = 0)
    enjoy_counter = models.IntegerField("Enjoy_counter", default = 0)
    coins = models.IntegerField("Diplodocoins", default = 0)    
    tkt_counter = models.IntegerField("tkt_counter", default=0)
    
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
    session_id = models.ForeignKey(Session, on_delete = models.CASCADE)
    skin = models.TextField("message_skin", default ="{}")

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


class Sound(models.Model): # Sound of the soundbox
    name = models.CharField("name", max_length=64)
    sound = models.FileField(upload_to="Soundbox/") 
    user = models.ForeignKey(User, on_delete=models.CASCADE) # L'utilisateur qui a fourni le son
    pub_date = models.DateField("Date publication", default = datetime.date.today) # Date d'enregistrement 
    tags = models.TextField('tags', default = '')
    counter = models.IntegerField(default=0)

    def __str__(self):
        return(f"{self.name}")


class UserSound(models.Model):
    sound = models.ForeignKey(Sound, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return(f"{self.sound} : {self.user}")
    
class Box(models.Model):
    name = models.CharField("name", max_length=64)
    image = models.ImageField(upload_to='Boxes/')
    open_price = models.IntegerField("Open price", default = 200)

    def __str__(self):
        return self.name
    
########### IL faudra suppr lors d'une prochaine migration ############
    def get_id(self):
        return self.id
    
class Rarity(models.Model):
    name = models.CharField("name", max_length=64)
    color = models.CharField("color", max_length=7, default = "#99E9E9")
    probability = models.FloatField("probability", default = 0.69)
    
    def __str__(self):
        return self.name
    
class Skin(models.Model):
    box = models.ForeignKey(Box, on_delete = models.CASCADE, null=True, blank=True)
    name = models.CharField("name", max_length=64)
    image = models.ImageField(upload_to='Skins/')
    rarity = models.ForeignKey(Rarity, on_delete = models.CASCADE, null=True, blank=True)
    TYPE = [('text_color', 'Text color'), ('border_color', 'Border color'), ('avatar_color', 'Avatar color'),
            ('name_color', 'Name color'), ('background_color', 'Background color'), ('background_image', 'Background image'),
            ('font', 'Font'), ('emoji', 'Emoji'), ('border_image', 'Border image'),
            ('name_rgb', 'Name RGB'), ('border_rgb', 'Border RGB'), 
            ('other', 'Other')]
    type = models.CharField("type", max_length=64, choices = TYPE, default = 'other')

    def __str__(self):
        return self.name
    

########### IL faudra changer le nom vers "Emoji" lors d'une prochaine migration ############
class Emojis(models.Model):
    name = models.CharField("name", max_length=64, unique=True)
    image = models.ImageField(upload_to = 'Emojis/')

    def __str__(self):
        return self.name

class Background(models.Model):
    name = models.CharField("name", max_length=64, unique=True)
    image = models.ImageField(upload_to = 'Backgrounds/')

    def __str__(self):
        return self.name
    
class Font(models.Model):
    name = models.CharField("name", max_length=64, unique=True)
    
    def __str__(self):
        return self.name
    
class BorderImage(models.Model):
    name = models.CharField("name", max_length=64, unique=True)
    image = models.ImageField(upload_to = 'BorderImages/')

    def __str__(self):
        return self.name

class Item(models.Model):
    TYPES = [('skin', 'Skin'), ('box', 'Box')]
    type = models.CharField("type", max_length=4, choices = TYPES, default = 'box')
    pattern = models.CharField("pattern", max_length=64, blank=True)
    item_id = models.IntegerField("item_id", default = 0)

    def __str__(self):
        return f"{self.type} {self.item_id} | {self.pattern}"

class UserInventory(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    item = models.OneToOneField(Item, on_delete = models.CASCADE)
    obtained_date = models.DateTimeField("obtained_date", default = datetime.datetime.now)
    favorite = models.BooleanField("favorite", default = False)
    equipped = models.BooleanField("equipped", default = False)

    def __str__(self):
        return f"{self.user} : {self.item}"

class Market(models.Model):
    seller = models.ForeignKey(User, on_delete = models.CASCADE)
    item = models.OneToOneField(Item, on_delete = models.CASCADE)
    price = models.IntegerField("price", default = 100)

    def __str__(self):
        return f"{self.seller} : {self.item} ({self.price})"

class MarketHistory(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    item = models.ForeignKey(Item, on_delete = models.CASCADE)
    price = models.IntegerField("price", default = 100)
    date = models.DateTimeField("Date de vente", default = datetime.datetime.today)
    ACTION = [('buy', 'Buy'), ('sell', 'Sell')]
    action = models.CharField("action", max_length=4, choices = ACTION, default = 'sell')

    def __str__(self):
        return f"{self.user} : {self.action} {self.item} ({self.price})"

class OpeningLog(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    skin = models.ForeignKey(Skin, on_delete = models.CASCADE)
    date = models.DateTimeField("Date d'ouverture", default = datetime.datetime.today)

    def __str__(self):
        return f"{self.user} : {self.skin} ({self.date})"    