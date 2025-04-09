from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import datetime
from django.utils import timezone
from Blog.views.karma_views import *
from django.conf import settings
from asgiref.sync import sync_to_async

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
    llm_context = models.TextField('llm_context', default='')
    
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

    pub_date = models.DateTimeField("Date publication", auto_now_add=True)
    writer = models.ForeignKey(User, on_delete = models.CASCADE)
    text = models.TextField("Texte")
    upvote = models.IntegerField("upvote", default = 0)
    downvote = models.IntegerField("downvote", default = 0)
    session_id = models.ForeignKey(Session, on_delete = models.CASCADE)
    skin = models.TextField("message_skin", default ="{}")
    karma = models.FloatField("karma", default = None, null=True)

    def __str__(self):
        return f"{self.writer} ({self.pub_date}) : {self.text}"
    
    def save(self, *args, **kwargs):
        if not self.karma:
            self.karma = analyze_sentiment(self.text)
        super().save(*args, **kwargs)

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
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True)

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



class Bot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    preprompt = models.TextField("preprompt", default="")
    model_name = models.CharField('model_name', default="mixtral-8x7b-32768", max_length=100)
    max_tokens = models.IntegerField('max_tokens', default=1024)
    temperature = models.FloatField('temperature', default=1.0)
    top_p = models.FloatField('top_p', default=0.95)
    presence_penalty = models.FloatField('presence_penalty', default=0.6)
    frequence_penalty = models.FloatField('frequence_penalty', default=0.6)
    is_callable = models.BooleanField(default=False)
    can_answer = models.BooleanField(default=True)

    def __str__(self):
        return f"Bot : {self.user.username}"


class SessionBot(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.bot} / {self.session}"
    
class EnjoyTimestamp(models.Model):
    time = models.TimeField()
    published_date = models.DateTimeField()
    writer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    comment = models.TextField()

    def __str__(self):
        return f"{self.time} ({self.writer.username})"

class Game(models.Model):
    name = models.CharField("name", max_length=64)
    SCORES = [(-1, 'None'), (0, 'Lowest is best'), (1, 'Highest is best')]
    score = models.IntegerField("score", choices = SCORES, default = -1)
    TYPES = [('solo', 'solo'), ('1v1', '1v1'), ('2v2', '2v2'), ('3v1', '3v1'), ('FFA', 'FFA')]
    gameType = models.CharField("gameType", max_length=4, default = "solo", choices = TYPES)

    def __str__(self):
        return self.name

class GameScore(models.Model):
    game = models.ForeignKey(Game, on_delete = models.CASCADE)
    score = models.FloatField()
    user = models.ForeignKey(User, null = True, on_delete=models.SET_NULL)
    date = models.DateTimeField(default=timezone.now)


class Pari(models.Model):
    name = models.CharField(max_length=100, null=False)
    description = models.TextField(default='', null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    published_date = models.DateTimeField(auto_now=True)
    duration = models.DurationField()
    open = models.BooleanField(default=True)
    admin_reviewed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.open})"

class PariIssue(models.Model):
    pari = models.ForeignKey(Pari, on_delete=models.CASCADE)
    issue = models.TextField()
    winning = models.BooleanField(default=None, null=True, blank=True)

    def __str__(self):
        return f"{self.issue} ({self.pari.name})"

class UserForIssue(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pari_issue = models.ForeignKey(PariIssue, on_delete=models.CASCADE)
    mise = models.IntegerField()
    comment = models.CharField(max_length=100, default='', null=True, blank=True)

    def __str__(self):
        return f"{self.user}_{self.pari_issue}"


class Lobby(models.Model):
    name = models.CharField(max_length=100, unique=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    token = models.CharField(max_length=16, default="")
    STATE = [('waiting', 'Waiting'), ('playing', 'Playing'), ('finished', 'Finished')]
    state = models.CharField(max_length=10, choices = STATE, default = 'waiting')
    mise = models.IntegerField(default=0)

    # Added async save method for asynchronous operations
    async def asave(self, *args, **kwargs):
        await sync_to_async(super(Lobby, self).save)(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.game}"


class ObjectifQuest(models.Model):
    type = models.CharField(max_length=64)  # Type d'objectif
    n_min = models.IntegerField()           # Nombre minimum à fournir
    n_max = models.IntegerField()           # Nombre maximum à fournir

    def __str__(self):
        return f"{self.type} ({self.n_min} - {self.n_max})"


class Quest(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)   # The user the quest is assigned
    CHOICES = [("box", "Box"), ("coins", "Coins")]             
    loot_type = models.CharField(choices=CHOICES, max_length=64) # The loot type of the quest (coin or box ?)
    quantity = models.IntegerField(default=1)                    # Quantity of loot
    start_date = models.DateTimeField(auto_now_add=True)         # Date of the beggining of the quest
    duration = models.DurationField()                            # Duration of the quest
    accepted = models.BooleanField(default = False)              # Is the quest accepted by the user ?
    achieved = models.BooleanField(default = False)              # Is the quest achieved ? 

    def __str__(self):
        return f"Quest {self.user.username} : {self.quantity} {self.loot_type} ({self.start_date})"


class ObjectifForQuest(models.Model):
    quest = models.ForeignKey(Quest, on_delete = models.CASCADE)
    objectif = models.ForeignKey(ObjectifQuest, on_delete=models.CASCADE)
    objective_value = models.IntegerField(default = 1) # Quantity of task to do
    current_value = models.IntegerField(default = 0)   # Current value you reached in your quest
    achieved = models.BooleanField(default = False)    # Is the objectif achieved ?

    def __str__(self):
        return f"{self.quest} - {self.objectif} ({self.objective_value})"

class DWAttack(models.Model):
    name = models.CharField(max_length=100)
    atk_mult_low = models.FloatField(default=0.5)
    atk_mult_high = models.FloatField(default=1.5)
    spe_effect = models.TextField(default='')

    def __str__(self):
        return self.name
    
class DWDino(models.Model):
    name = models.CharField(max_length=100)
    CLASS = [('tank', 'Tank'), ('dps', 'DPS'), ('support', 'Support')]
    classe = models.CharField(max_length=10, choices=CLASS, default='dps')
    base_hp = models.IntegerField(default=3000)
    base_atk = models.IntegerField(default=100)
    base_def = models.IntegerField(default=100)
    base_spd = models.FloatField(default=1.0)
    base_crit = models.FloatField(default=0.05)
    base_crit_dmg = models.FloatField(default=1.5)
    attack = models.ForeignKey(DWAttack, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name
    
class DWUserDino(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dino = models.ForeignKey(DWDino, on_delete=models.CASCADE)
    level = models.IntegerField(default=1)
    hp = models.IntegerField(default=3000)
    atk = models.IntegerField(default=100)
    defense = models.IntegerField(default=100)
    spd = models.FloatField(default=1.0)
    crit = models.FloatField(default=0.05)
    crit_dmg = models.FloatField(default=1.5)
    attack = models.ForeignKey(DWAttack, on_delete=models.CASCADE, null=True, blank=True)
    in_arena = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.dino} de {self.user} (lvl{self.level})"

class DWUserTeam(models.Model):
    name = models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dino1 = models.ForeignKey(DWUserDino, on_delete=models.CASCADE, related_name='dino1')
    dino2 = models.ForeignKey(DWUserDino, on_delete=models.CASCADE, related_name='dino2')
    dino3 = models.ForeignKey(DWUserDino, on_delete=models.CASCADE, related_name='dino3')
    in_arena = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.dino1} - {self.dino2} - {self.dino3}"
    
class DWUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    elo = models.IntegerField(default=1000)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    free_hatch = models.IntegerField(default=0)
    arena_energy = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} ({self.elo}elo)"

class DWArena(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    team = models.ForeignKey(DWUserTeam, null=True, blank=True, on_delete=models.SET_NULL)
    user_str = models.CharField(max_length=100, default='')
    team_str = models.CharField(max_length=100, default='')
    date = models.DateTimeField(auto_now_add=True)
    win_streak = models.IntegerField(default=1)
    active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.user:
            self.user_str = self.user.username
        if self.team:
            self.team_str = str(self.team)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user_str} ({self.team_str})"

class DWFight(models.Model):
    user1 = models.CharField(max_length=100)
    user2 = models.CharField(max_length=100)
    user1_team = models.CharField(max_length=100)
    user2_team = models.CharField(max_length=100)
    winner = models.CharField(max_length=100)
    GAMEMODE = [('duel', 'Duel'), ('arena', 'Arena')]
    gamemode = models.CharField(max_length=10, choices=GAMEMODE, default='duel')
    date = models.DateTimeField(auto_now_add=True)
    logs = models.TextField(default='')
    
    def __str__(self):
        return f"{self.user1} vs {self.user2} ({self.date})"
    
class DWDinoItem(models.Model):
    SLOT_TYPES = [
        ('hp', 'Health'),
        ('atk', 'Attack'),
        ('defense', 'Defense'),
        ('spd', 'Speed'),
        ('crit', 'Critical Rate'),
        ('crit_dmg', 'Critical Damage'),
    ]
    
    dino = models.ForeignKey(DWUserDino, on_delete=models.CASCADE)
    slot = models.CharField(max_length=8, choices=SLOT_TYPES)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('dino', 'slot')
        
    def __str__(self):
        return f"{self.dino} - {self.get_slot_display()}: {self.item}"