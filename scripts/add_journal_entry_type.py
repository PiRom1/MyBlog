from django.db import transaction, IntegrityError
from Blog.models import JournalEntryType, JournalEntryTypeForUser, User

ENTRY_TYPE = 'Collection'


def run():
    try:
        with transaction.atomic():
            entry_type, created = JournalEntryType.objects.get_or_create(
                entry_type=ENTRY_TYPE
            )
            if not created:
                print(f"Le type {ENTRY_TYPE} existait déjà (id={entry_type.pk})")

            deja_lies = set(
                JournalEntryTypeForUser.objects
                .filter(entry_type=entry_type)
                .values_list('user_id', flat=True)
            )

            a_creer = [
                JournalEntryTypeForUser(
                    entry_type=entry_type, user=user, get_notification=True
                )
                for user in User.objects.exclude(pk__in=deja_lies)
            ]

            JournalEntryTypeForUser.objects.bulk_create(a_creer, ignore_conflicts=True)
            print(f"{len(a_creer)} liaisons créées pour {ENTRY_TYPE}")

    except IntegrityError as e:
        print(f"Erreur : {e}")