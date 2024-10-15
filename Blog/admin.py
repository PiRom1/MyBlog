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
    fieldsets[1][1]['fields'] += ('yoda_counter',)
    fieldsets[1][1]['fields'] += ('enjoy_counter',)
    fieldsets[1][1]['fields'] += ('coins',)
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

@admin.register(Sondage)
class SondageAdmin(admin.ModelAdmin):
    list_display = ('question', 'pub_date')

@admin.register(SondageChoice)
class SondageChoiceAdmin(admin.ModelAdmin):
    list_display = ('choice','sondage','votes')

@admin.register(ChoiceUser)
class ChoiceUserAdmin(admin.ModelAdmin):
    list_display = ('choice','user')

@admin.register(Recit)
class Recitadmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Texte)
class TexteAdmin(admin.ModelAdmin):
    list_display = ('text', 'user', 'recit')


@admin.register(Sound)
class SoundAdmin(admin.ModelAdmin):
    list_display = ('name', 'sound', 'user', 'counter', 'pub_date', 'tags')


@admin.register(UserSound)
class UserSoundAdmin(admin.ModelAdmin):
    list_display = ('sound', 'user')

@admin.register(Boxes)
class BoxesAdmin(admin.ModelAdmin):
    list_display = ('name', 'image', 'price')

@admin.register(Skins)
class SkinsAdmin(admin.ModelAdmin):
    list_display = ('box', 'name', 'image', 'pattern')

@admin.register(UserInventory)
class UserInventoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'item_id', 'status')

@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ('seller', 'type', 'item_id', 'price')
