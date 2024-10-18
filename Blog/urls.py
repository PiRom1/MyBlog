from django.urls import path, include
from .views import chat_views, recits_views, lootbox_views, sondages_views, soundbox_views, tickets_views, user_views, utils_views, inventory_views

urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),

    path("", utils_views.getSession, name = "get_session"),
    path("<int:id>/", chat_views.Index, name="index"),
    path("login/", user_views.connexion, name = "login"),
    path("logout/", user_views.deconnexion, name = "logout"),
    path("invalid_user/", user_views.InvalidUser, name = "invalid_user"),
    path("stats/<int:id>/", chat_views.Stats, name="stats"),
    path("user/<int:id>/", user_views.UserView, name="user"),
    path("user/<int:id>/messages", chat_views.IndexUser, name="index_user"),
    path("user/<int:id>/messages/<str:word>", chat_views.IndexUserMessage, name="index_user_message"),
    path('change_photo', user_views.change_photo, name = 'change_photo'),
    #path("dark_mode/", views.dark_mode, name = "dark_mode")
    # path("add_user/", views.AddUser, name = "add_user"),
    # path("upvote/<int:message_id>/", views.upvote, name = "upvote"),
    # path("downvote/<int:message_id>/", views.downvote, name = "downvote"),
    # path("modify/<int:message_id>/", views.Modify, name = "modify"),

    # TICKETS #
    path('tickets/', tickets_views.ticket_list, name='ticket_list'),
    path('tickets/create/', tickets_views.create_ticket, name='create_ticket'),
    path('tickets/update/<int:pk>/', tickets_views.update_ticket, name='update_ticket'),
   

    # SONDAGES #
    path('sondages/', sondages_views.sondage_list, name='sondage_list'),
    path('sondages/create/', sondages_views.create_sondage, name='create_sondage'),
    path('sondages/update/<int:pk>/', sondages_views.update_sondage, name='update_sondage'),
    path('sondages/delete/<int:pk>/', sondages_views.delete_sondage, name='delete_sondage'),
    path('sondages/detail/<int:pk>/', sondages_views.detail_sondage, name='detail_sondage'),
    path('sondages/vote/<int:sondage_id>/<int:choice_id>/', sondages_views.vote_sondage, name = 'vote_sondage'),

    # Récits
    path('recits/', recits_views.recit_list, name='recit_list'),
    path('recits/create/', recits_views.create_recit, name='create_recit'),
    path('recits/detail/<int:pk>/', recits_views.detail_recit, name='detail_recit'),

    # Lootbox
    path('lootbox/<int:pk>', lootbox_views.view_lootbox, name='view_lootbox'),  
    path('lootbox/open', lootbox_views.open_lootbox, name='open_lootbox'),  
    path('lootbox/drop_item', lootbox_views.drop_item, name='drop_item'),  
    path('lootbox/get', lootbox_views.get_lootbox, name='get_lootbox'),
    
    # Inventory
    path('inventory/', inventory_views.user_inventory_view, name='inventory'),
    path('inventory/toggle_item_status', inventory_views.toggle_item_status, name='toggle_item_status'),

    # Soundbox
    path('list_sounds', soundbox_views.list_sounds, name='list_sounds'),
    path('add_sounds', soundbox_views.add_sounds, name='add_sounds'),

    # Other
    path('increment_yoda/', chat_views.increment_yoda, name='increment_yoda'),
    path('increment_enjoy/', chat_views.increment_enjoy, name='increment_enjoy'),
    path('increment_sound/', soundbox_views.increment_sound, name='increment_sound'),
    path('tkt/', chat_views.tkt_view, name='tkt'),
    path('update_plot/', user_views.update_plot, name='update_plot'),
    path('update_soundbox/', soundbox_views.update_soundbox, name='update_soundbox'),
    
]