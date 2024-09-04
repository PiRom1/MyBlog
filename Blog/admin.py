from typing import Any
from django.contrib import admin
from django.http import HttpRequest
from .models import *
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.db.models.functions import Lower, Reverse
class UserAdmin(DefaultUserAdmin):
    model = User
    list_display = ['username', 'is_superuser']
    fieldsets = DefaultUserAdmin.fieldsets
    fieldsets[1][1]['fields'] += ('image',)
    add_fieldsets = DefaultUserAdmin.add_fieldsets 

admin.site.register(User, UserAdmin)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('pub_date', 'writer', 'text')
    
@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('session_name',)

@admin.register(SessionUser)
class SessionUserAdmin(admin.ModelAdmin):
    list_display = ('session', 'user')

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('image',)

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'status',)

    def get_ordering(self, request):
        return ['-status']
