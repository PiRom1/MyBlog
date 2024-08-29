from django.db import models
from django.contrib.auth.models import User, AbstractUser, BaseUserManager

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

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    objects = UserManager()
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Utilisateur'

    def __str__(self):
        return f'{self.username}'
    

class Session(models.Model):
    session_name = models.TextField("name", default = "")
    session_id = models.AutoField(primary_key=True)

    def __str__(self):
        return f"{self.session_name} ({self.session_id})"

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
    session_id = models.IntegerField("session_id", default = 0)

    def __str__(self):
        return f"{self.writer} ({self.pub_date}) : {self.text}"

class History(models.Model):

    pub_date = models.DateTimeField("Date modification")
    writer = models.ForeignKey(User, on_delete = models.CASCADE)
    text = models.TextField("Texte")
    message = models.ForeignKey(Message, on_delete = models.CASCADE)


class Photo(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='Images/')