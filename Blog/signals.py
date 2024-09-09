
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_save
from rest_framework.authtoken.models import Token
from .models import ChoiceUser, SondageChoice

@receiver(post_save, sender=settings.AUTH_USER_MODEL, dispatch_uid="user_auth_token")
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=ChoiceUser)
def increment_vote(sender, instance, created, **kwargs):
    if created:
        # Incrémente le champ nombre_vote
        sondage_choice = instance.choice
        sondage_choice.votes += 1
        sondage_choice.save()

@receiver(post_delete, sender=ChoiceUser)
def decrement_vote(sender, instance, **kwargs):
    # Décrémente le champ nombre_vote
    sondage_choice = instance.choice
    sondage_choice.votes -= 1
    sondage_choice.save()

@receiver(pre_save, sender=ChoiceUser)
def handle_vote_change(sender, instance, **kwargs):
    if instance.pk:
        # Si l'instance existe déjà (donc pas un nouvel enregistrement)
        previous_instance = ChoiceUser.objects.get(pk=instance.pk)
        if previous_instance.choice != instance.choice:
            # Si le choix a changé, on décrémente l'ancien choix
            old_choice = previous_instance.choice
            old_choice.votes -= 1
            old_choice.save()

            instance.choice.votes += 1
            instance.choice.save()


