from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
class UserAdmin(DefaultUserAdmin):
    model = User
    list_display = ['username', 'is_superuser']
    fieldsets = DefaultUserAdmin.fieldsets
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
