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
    list_filter = ('pub_date', 'writer', 'session_id')
    search_fields = ('text', 'writer__username')
    
@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('session_name',)
    search_fields = ('session_name',)

@admin.register(SessionUser)
class SessionUserAdmin(admin.ModelAdmin):
    list_display = ('session', 'user')
    list_filter = ('session', 'user')
    search_fields = ('session__session_name', 'user__username')

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('image',)
    search_fields = ('image',)

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'status',)
    list_filter = ('status', 'category', 'created_at', 'assigned_to')
    search_fields = ('title', 'description', 'created_by__username')

    def get_ordering(self, request):
        return ['-status']

@admin.register(Sondage)
class SondageAdmin(admin.ModelAdmin):
    list_display = ('question', 'pub_date')
    list_filter = ('pub_date', 'current', 'session')
    search_fields = ('question',)

@admin.register(SondageChoice)
class SondageChoiceAdmin(admin.ModelAdmin):
    list_display = ('choice','sondage','votes')
    list_filter = ('sondage',)
    search_fields = ('choice', 'sondage__question')

@admin.register(ChoiceUser)
class ChoiceUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'choice')
    list_filter = ('user', 'choice__sondage')
    search_fields = ('user__username', 'choice__choice')

@admin.register(Recit)
class Recitadmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Texte)
class TexteAdmin(admin.ModelAdmin):
    list_display = ('text', 'user', 'recit')
    list_filter = ('user', 'recit')
    search_fields = ('text', 'user__username', 'recit__name')

@admin.register(Sound)
class SoundAdmin(admin.ModelAdmin):
    list_display = ('name', 'sound', 'user', 'counter', 'pub_date', 'tags')
    list_filter = ('user', 'pub_date')
    search_fields = ('name', 'tags', 'user__username')

@admin.register(UserSound)
class UserSoundAdmin(admin.ModelAdmin):
    list_display = ('sound', 'user')
    list_filter = ('user',)
    search_fields = ('sound__name', 'user__username')

@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ('name', 'image', 'open_price')
    list_filter = ('open_price',)
    search_fields = ('name',)

@admin.register(Rarity)
class RarityAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'probability')
    list_filter = ('probability',)
    search_fields = ('name', 'color')

@admin.register(Skin)
class SkinAdmin(admin.ModelAdmin):
    list_display = ('id', 'box', 'name', 'image', 'rarity', 'type')
    list_filter = ('box', 'rarity', 'type')
    search_fields = ('name', 'box__name')
    
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'item_id', 'pattern')
    list_filter = ('type',)
    search_fields = ('pattern',)

@admin.register(UserInventory)
class UserInventoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'item', 'obtained_date', 'favorite', 'equipped')
    list_filter = ('user', 'favorite', 'equipped', 'obtained_date')
    search_fields = ('user__username',)

@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ('seller', 'item', 'price')
    list_filter = ('seller', 'price')
    search_fields = ('seller__username',)

@admin.register(MarketHistory)
class MarketHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'price', 'date', 'action')
    list_filter = ('action', 'date', 'user')
    search_fields = ('user__username',)

@admin.register(Emojis)
class EmojisAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'image')
    search_fields = ('name',)

@admin.register(Background)
class BackgroundAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'image')
    search_fields = ('name',)

@admin.register(BorderImage)
class BorderImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'image')
    search_fields = ('name',)

@admin.register(Font)
class FontAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    search_fields = ('name',)

@admin.register(OpeningLog)
class OpeningLogsAdmin(admin.ModelAdmin):
    list_display = ('user', 'skin', 'date')
    list_filter = ('user', 'date')
    search_fields = ('user__username', 'skin__name')

@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    list_display = ('user', 'preprompt', 'model_name', 'max_tokens', 'temperature', 'top_p', 'presence_penalty', 'frequence_penalty', 'can_answer', 'is_callable')
    list_filter = ('model_name', 'can_answer', 'is_callable')
    search_fields = ('user__username', 'preprompt')

@admin.register(SessionBot)
class SessionBotAdmin(admin.ModelAdmin):
    list_display = ('session', 'bot')
    list_filter = ('session', 'bot')
    search_fields = ('session__session_name', 'bot__user__username')

@admin.register(EnjoyTimestamp)
class EnjoyTimestampAdmin(admin.ModelAdmin):
    list_display = ('time', 'published_date', 'writer', 'comment')
    list_filter = ('published_date', 'writer')
    search_fields = ('comment', 'writer__username')

@admin.register(GameScore)
class GameScoreAdmin(admin.ModelAdmin):
    list_display = ('game', 'score', 'user', 'date')
    list_filter = ('game', 'user', 'date')
    search_fields = ('user__username', 'game__name')

@admin.register(Pari)
class PariAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'creator', 'open', 'admin_reviewed')
    list_filter = ('open', 'admin_reviewed', 'creator')
    search_fields = ('name', 'description', 'creator__username')

@admin.register(PariIssue)
class PariIssueAdmin(admin.ModelAdmin):
    list_display = ('pari', 'issue', 'winning')
    list_filter = ('pari', 'winning')
    search_fields = ('issue', 'pari__name')

@admin.register(UserForIssue)
class UserForIssueAdmin(admin.ModelAdmin):
    list_display = ('user', 'pari_issue', 'mise')
    list_filter = ('user', 'pari_issue__pari')
    search_fields = ('user__username', 'comment')

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'gameType', 'score')
    list_filter = ('gameType', 'score')
    search_fields = ('name',)

@admin.register(Lobby)
class LobbyAdmin(admin.ModelAdmin):
    list_display = ('name', 'game', 'created_at', 'token', 'state', 'mise')
    list_filter = ('game', 'state', 'created_at')
    search_fields = ('name', 'token')

@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    list_display = ("user", "loot_type", "quantity", "start_date", "duration", "accepted", "achieved")
    list_filter = ("user", "loot_type", "accepted", "achieved", "start_date")
    search_fields = ("user__username",)

@admin.register(ObjectifQuest)
class ObjectifQuestAdmin(admin.ModelAdmin):
    list_display = ("type", "n_min", "n_max")
    list_filter = ("type",)
    search_fields = ("type",)

@admin.register(ObjectifForQuest)
class ObjectifForQuestAdmin(admin.ModelAdmin):
    list_display = ("quest", "objectif", "achieved", "objective_value", "current_value")
    list_filter = ("achieved", "objectif", "quest__user")
    search_fields = ("quest__user__username", "objectif__type")

@admin.register(DWAttack)
class DWAttackAdmin(admin.ModelAdmin):
    list_display = ('name', 'atk_mult_low', 'atk_mult_high', 'spe_effect')
    search_fields = ('name', 'spe_effect')

@admin.register(DWDino)
class DWDinoAdmin(admin.ModelAdmin):
    list_display = ('name', 'classe', 'base_hp', 'base_atk', 'base_def', 'base_spd', 'base_crit', 'base_crit_dmg', 'attack')
    list_filter = ('classe',)
    search_fields = ('name',)

@admin.register(DWUserDino)
class DWUserDinoAdmin(admin.ModelAdmin):
    list_display = ('user', 'dino', 'level', 'hp', 'atk', 'defense', 'spd', 'crit', 'crit_dmg', 'attack', 'in_arena')
    list_filter = ('user', 'dino', 'level', 'in_arena')
    search_fields = ('user__username', 'dino__name')

@admin.register(DWUserTeam)
class DWUserTeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'dino1', 'dino2', 'dino3', 'in_arena')
    list_filter = ('user', 'in_arena')
    search_fields = ('name', 'user__username')

@admin.register(DWUser)
class DWUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'elo', 'wins', 'losses', 'free_hatch', 'arena_energy', 'free_pvm', 'pvm_runs_td')
    list_filter = ('free_hatch', 'arena_energy')
    search_fields = ('user__username',)

@admin.register(DWFight)
class DWFightAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2', 'winner', 'gamemode', 'date')
    list_filter = ('gamemode', 'date')
    search_fields = ('user1', 'user2', 'winner')

@admin.register(DWDinoItem)
class DWDinoItemAdmin(admin.ModelAdmin):
    list_display = ('dino', 'slot', 'item')
    list_filter = ('slot',)
    search_fields = ('dino__user__username', 'dino__dino__name')

@admin.register(DWArena)
class DWArenaAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'user_str', 'team_str', 'win_streak', 'date', 'active')
    list_filter = ('active', 'win_streak')
    search_fields = ('user_str', 'team_str')

@admin.register(DWPvmDino)
class DWPvmDinoAdmin(admin.ModelAdmin):
    list_display = ('user', 'dino', 'hp', 'atk', 'defense', 'spd', 'crit', 'crit_dmg', 'attack')
    list_filter = ('user', 'dino')
    search_fields = ('user__username', 'dino__name')

@admin.register(DWPvmAbility)
class DWPvmAbilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

@admin.register(DWPvmRun)
class DWPvmRunAdmin(admin.ModelAdmin):
    list_display = ('user', 'dino1', 'dino2', 'dino3', 'life', 'level', 'stat_points', 'run_date', 'seen_abilities')
    list_filter = ('user', 'level')
    search_fields = ('user__username',)

@admin.register(DWPvmRunAbility)
class DWPvmRunAbilityAdmin(admin.ModelAdmin):
    list_display = ('run', 'ability')
    list_filter = ('ability',)
    search_fields = ('run__user__username', 'ability__name')

@admin.register(DWPvmNextFightDino)
class DWPvmNextFightDinoAdmin(admin.ModelAdmin):
    list_display = ('run', 'dino', 'hp', 'atk', 'defense', 'spd', 'crit', 'crit_dmg', 'attack')
    list_filter = ('run__user', 'dino')
    search_fields = ('run__user__username', 'dino__name')

@admin.register(DWPvmNextAbility)
class DWPvmNextAbilityAdmin(admin.ModelAdmin):
    list_display = ('run', 'ability')
    list_filter = ('run__user', 'ability')
    search_fields = ('run__user__username', 'ability__name')

@admin.register(DWPvmNewRun)
class DWPvmNewRunAdmin(admin.ModelAdmin):
    list_display = ('user', 'state', 'dino1', 'dino2', 'dino3', 'date')
    list_filter = ('user',)
    search_fields = ('user__username',)

@admin.register(DWPvmTerrain)
class DWPvmTerrainAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

@admin.register(DWPvmLeaderboard)
class DWPvmLeaderboardAdmin(admin.ModelAdmin):
    list_display = ('user', 'terrain', 'date', 'run_level', 'team_dinos_stats', 'abilities_list')
    list_filter = ('user', 'terrain')
    search_fields = ('user__username', 'terrain__name')