from django.contrib import admin
from .models import Message, Session
# Register your models here.

from django.contrib import admin

class MessageAdmin(admin.ModelAdmin):
    list_display = ('pub_date', 'writer', 'text')

class SessionAdmin(admin.ModelAdmin):
    list_display = ('session_id',)

admin.site.register(Message,MessageAdmin)
admin.site.register(Session,SessionAdmin)