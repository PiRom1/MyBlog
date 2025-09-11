from Blog.models import JournalEntry, JournalEntryType, JournalEntryTypeForUser, User

def run():

    # Define JournalEntryType

    JournalEntryType.objects.get_or_create(entry_type = 'Arène')
    JournalEntryType.objects.get_or_create(entry_type = 'HDV')
    JournalEntryType.objects.get_or_create(entry_type = 'Pari')
    JournalEntryType.objects.get_or_create(entry_type = 'Quête')
    JournalEntryType.objects.get_or_create(entry_type = 'Ticket')
    JournalEntryType.objects.get_or_create(entry_type = 'Récit')
    JournalEntryType.objects.get_or_create(entry_type = 'Sondage')
    JournalEntryType.objects.get_or_create(entry_type = 'Soundbox')
    JournalEntryType.objects.get_or_create(entry_type = 'Tag')

    for user in User.objects.all():
        for entry_type in JournalEntryType.objects.all():
            JournalEntryTypeForUser.objects.get_or_create(user = user,
                                                          entry_type = entry_type)
    
