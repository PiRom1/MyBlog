import json
from Blog.models import User, JournalEntry, JournalEntryType, JournalEntryTypeForUser
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from numpy import ceil
from django.contrib.auth.decorators import login_required


@login_required
def get_journal_entries(request):

    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return HttpResponseBadRequest('<h1>400 Bad Request</h1><p>Requête non autorisée.</p>')
    

    try:
        user = request.user

        page = int(request.GET.get('page', 1))
        nb_per_page = int(request.GET.get('nb_per_page', 10))
        entries_by_page = nb_per_page
        
        notifying_journal_entrytypes = JournalEntryTypeForUser.objects.filter(user = user, get_notification=True)
        notifying_journal_entrytypes = [entry_type.entry_type for entry_type in notifying_journal_entrytypes]
        all_journal_entries = JournalEntry.objects.filter(user = user, entry_type__in=notifying_journal_entrytypes).order_by('-date')

        
        can_increase_page = len(all_journal_entries) > page*entries_by_page
        n_pages = ceil(len(all_journal_entries)/entries_by_page)
        
        all_journal_entries_page = all_journal_entries[((page-1)*entries_by_page):(page*entries_by_page)]
        
        for entry in all_journal_entries_page:
            entry.is_viewed=True
            entry.save()

        data = {'all_journal_entries' : [{'entry' : entry.entry ,
                                          'entry_type' : entry.entry_type.entry_type,
                                          'date' : entry.date.strftime('%d/%m/%y %H:%M'),
                                          'is_viewed' : entry.is_viewed,} for entry in all_journal_entries_page],
                'notifying_journal_entrytypes' : [entry_type.entry_type for entry_type in notifying_journal_entrytypes],
                'can_increase_page' : can_increase_page,
                'can_decrease_page' : page > 1,
                'n_pages' : n_pages,}
        
        
        
        return JsonResponse({'success' : True, 
                            'data' : data})

    except Exception as e:
        print(e)
        return JsonResponse({'success' : False,
                             'error' : str(e)})

@login_required
def get_notifications_number(request):

    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return HttpResponseBadRequest('<h1>400 Bad Request</h1><p>Requête non autorisée.</p>')
    
    notifying_journal_entrytypes = JournalEntryTypeForUser.objects.filter(user = request.user, get_notification=True)
    notifying_journal_entrytypes = [entry_type.entry_type for entry_type in notifying_journal_entrytypes]
    
    return JsonResponse({'success' : True, 
                         'data' : {'nb_notifications' : JournalEntry.objects.filter(user = request.user, is_viewed = False, entry_type__in=notifying_journal_entrytypes).count()}
                        })


@login_required
def manage_notification_entry(request):

    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            return HttpResponseBadRequest('<h1>400 Bad Request</h1><p>Requête non autorisée.</p>')
        
    data = json.loads(request.body)

    try:
        label = data['label']

        entry_type = JournalEntryType.objects.get(entry_type=label)

        entry_type_for_user = JournalEntryTypeForUser.objects.filter(user=request.user, entry_type = entry_type).first()
        entry_type_for_user.get_notification = not entry_type_for_user.get_notification
        entry_type_for_user.save()
    
        return JsonResponse({'success' : True})
    
    except:
        return JsonResponse({'success' : False})


