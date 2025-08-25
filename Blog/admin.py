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
    fieldsets[1][1]['fields'] += ('tkt_counter',)
    fieldsets[1][1]['fields'] += ('llm_context',)
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
    list_display = ('user', 'choice')

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

@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ('name', 'image', 'open_price')

@admin.register(Rarity)
class RarityAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'probability')

@admin.register(Skin)
class SkinAdmin(admin.ModelAdmin):
    list_display = ('id', 'box', 'name', 'image', 'rarity', 'type')
    
    
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'item_id', 'pattern')

@admin.register(UserInventory)
class UserInventoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'item', 'obtained_date', 'favorite', 'equipped')

@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ('seller', 'item', 'price')

@admin.register(MarketHistory)
class MarketHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'price', 'date', 'action')


@admin.register(Emojis)
class EmojisAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'image')

@admin.register(Background)
class BackgroundAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'image')

@admin.register(BorderImage)
class BorderImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'image')

@admin.register(Font)
class FontAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)

@admin.register(OpeningLog)
class OpeningLogsAdmin(admin.ModelAdmin):
    list_display = ('user', 'skin', 'date')


@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    list_display = ('user', 'preprompt', 'model_name', 'max_tokens', 'temperature', 'top_p', 'presence_penalty', 'frequence_penalty', 'can_answer', 'is_callable', )


@admin.register(SessionBot)
class SessionBotAdmin(admin.ModelAdmin):
    list_display = ('session', 'bot')


@admin.register(EnjoyTimestamp)
class EnjoyTimestampAdmin(admin.ModelAdmin):
    list_display = ('time', 'published_date', 'writer', 'comment', 'note')


@admin.register(GameScore)
class GameScoreAdmin(admin.ModelAdmin):
    list_display = ('game', 'score', 'user', 'date')


@admin.register(Pari)
class PariAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'creator', 'open', 'admin_reviewed')


@admin.register(PariIssue)
class PariAdmin(admin.ModelAdmin):
    list_display = ('pari', 'issue', 'winning')


@admin.register(UserForIssue)
class UserForIssueAdmin(admin.ModelAdmin):
    list_display = ('user', 'pari_issue', 'mise')
@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'gameType', 'score')

@admin.register(Lobby)
class LobbyAdmin(admin.ModelAdmin):
    list_display = ('name', 'game', 'created_at', 'token', 'state', 'mise')

@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    list_display = ("user", "loot_type", "quantity", "start_date", "duration", "accepted", "achieved")


@admin.register(ObjectifQuest)
class ObjectifQuestAdmin(admin.ModelAdmin):
    list_display = ("type", "n_min", "n_max")


@admin.register(ObjectifForQuest)
class ObjectifForQuestAdmin(admin.ModelAdmin):
    list_display = ("quest", "objectif", "achieved", "objective_value", "current_value")


@admin.register(JournalEntryType)
class JournalEntryTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "entry_type")

@admin.register(JournalEntryTypeForUser)
class JournalEntryTypeForUserAdmin(admin.ModelAdmin):
    list_display = ("id", "entry_type", "user", "get_notification")

@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "entry_type", "user", "entry", "date", "is_viewed")
    

@admin.register(DWAttack)
class DWAttackAdmin(admin.ModelAdmin):
    list_display = ('name', 'atk_mult_low', 'atk_mult_high', 'spe_effect')

@admin.register(DWDino)
class DWDinoAdmin(admin.ModelAdmin):
    list_display = ('name', 'classe', 'base_hp', 'base_atk', 'base_def', 'base_spd', 'base_crit', 'base_crit_dmg', 'attack')

@admin.register(DWUserDino)
class DWUserDinoAdmin(admin.ModelAdmin):
    list_display = ('user', 'dino', 'level', 'hp', 'atk', 'defense', 'spd', 'crit', 'crit_dmg', 'attack', 'in_arena')

@admin.register(DWUserTeam)
class DWUserTeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'dino1', 'dino2', 'dino3', 'in_arena')

@admin.register(DWUser)
class DWUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'elo', 'wins', 'losses', 'free_hatch', 'arena_energy')

@admin.register(DWFight)
class DWFightAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2', 'winner', 'gamemode', 'date')

@admin.register(DWDinoItem)
class DWDinoItemAdmin(admin.ModelAdmin):
    list_display = ('dino', 'slot', 'item')

@admin.register(DWArena)
class DWArenaAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'user_str', 'team_str', 'win_streak', 'date', 'active')