from django.shortcuts import render, redirect
from ..models import *
from ..forms import *
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings


from ..utils.stats import *



@login_required
def ticket_list(request):
    tickets = Ticket.objects.all()
    open_tickets = tickets.filter(status='open')
    closed_tickets = tickets.filter(status='closed')
    in_progress_tickets = tickets.filter(status='in_progress')
    print(tickets)
    print(open_tickets)
    return render(request, 'Blog/tickets/ticket_list.html', {'tickets': tickets,
                                                             'open_tickets': open_tickets,
                                                             'closed_tickets': closed_tickets,
                                                             'in_progress_tickets': in_progress_tickets})

@login_required
def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()

            subject = 'Nouveau ticket : ' + ticket.title
            email_from = settings.EMAIL_HOST_USER
            if ticket.assigned_to and ticket.assigned_to.email:
                recipient_list = [ticket.assigned_to.email, ]
                message = f"""Hey {ticket.assigned_to.username},\n\n
                            Un nouveau ticket t\'a été assigné par {ticket.created_by.username} !\n
                            Tu peux le consulter à l'adresse suivante : https://diplo.pythonanywhere.com/tickets/update/{ticket.id}/"""
            elif ticket.created_by.email:
                recipient_list = [ticket.created_by.email, ]
                message = f'Hey {ticket.created_by.username}, malheureusement la personne à qui tu as assigné le ticket n\'a pas d\'adresse mail valide.'
            else:
                return redirect('ticket_list')
            send_mail( subject, message, email_from, recipient_list )

            return redirect('ticket_list')
    else:
        form = TicketForm()
        # préremplir le champ titre avec le texte du dernier message si il commence par "Nouveau ticket :"
        last_message = Message.objects.last()
        code = (last_message.text.split(':')[0]).lower().strip()
        if code == "nouveauticket":
            form.fields['title'].initial = last_message.text.split(':',1)[1]
            last_message.delete()
    return render(request, 'Blog/tickets/create_ticket.html', {'form': form})

@login_required
def update_ticket(request, pk):
    ticket = Ticket.objects.get(pk=pk)
    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('ticket_list')
    else:
        form = TicketForm(instance=ticket)
    return render(request, 'Blog/tickets/update_ticket.html', {'form': form, 'ticket': ticket})

