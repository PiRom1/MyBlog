from django.urls import path, include
from .views import chat_views, recits_views, lootbox_views, sondages_views, soundbox_views, tickets_views, user_views, utils_views, inventory_views, inventory_2_views, hdv_views, enjoy_timeline_views, jeux_views, paris_views, quests_views, atelier_views

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
    path('inventory/toggle_item_favorite', inventory_views.toggle_item_favorite, name='toggle_item_favorite'),
    path('inventory/favorite', inventory_views.get_favorite_skins, name='get_favorite_skins'),
    path('inventory/update_equipped', inventory_views.update_equipped, name='update_equipped'),
    path('equip_bg', inventory_views.equip_bg, name='equip_bg'),
    path('unequip_bg', inventory_views.unequip_bg, name='unequip_bg'),

    # Emojis
    path('emoji/<int:pk>', inventory_views.use_emoji, name='use_emoji'),

    # Background
    path('background/<int:pk>', inventory_views.use_bg, name='use_bg'),
    
    # Inventory_2
    path('inventory_2/', inventory_2_views.user_inventory_view, name='inventory'),
    path('inventory_2/toggle_item_status', inventory_2_views.toggle_item_status, name='toggle_item_status'),

    # HDV
    path('hdv', hdv_views.list_hdv, name ='hdv'),
    path('hdv/buy', hdv_views.buy, name='buy'),
    path('hdv/sell', hdv_views.sell, name='sell'),
    path('hdv/remove', hdv_views.remove, name='remove'),

    # Soundbox
    path('list_sounds', soundbox_views.list_sounds, name='list_sounds'),
    path('add_sounds', soundbox_views.add_sounds, name='add_sounds'),

    # Enjoy Timeline
    path('enjoy_timeline/', enjoy_timeline_views.enjoy_timeline, name='enjoy_timeline'),
    path('enjoy_timeline/<int:hour>/<int:minute>/', enjoy_timeline_views.enjoy_timeline_hour_minute, name='enjoy_timeline_hour_minute'),

    # Bot
    path('bot/<int:id>/chat/', chat_views.chat_with_bot, name="chat_with_bot"),

    # Other
    path('increment_yoda/', chat_views.increment_yoda, name='increment_yoda'),
    path('increment_enjoy/', chat_views.increment_enjoy, name='increment_enjoy'),
    path('increment_sound/', soundbox_views.increment_sound, name='increment_sound'),
    path('tkt/', chat_views.tkt_view, name='tkt'),
    path('update_plot/', user_views.update_plot, name='update_plot'),
    path('update_soundbox/', soundbox_views.update_soundbox, name='update_soundbox'),
    path('ask_heure_enjoy/', chat_views.ask_heure_enjoy, name = 'ask_heure_enjoy'),
    path('get_moderaptor/', utils_views.get_moderaptor, name = 'get_moderaptor'),

    # Jeux
    path('jeux/', jeux_views.list_jeux, name = 'list_jeux'),
    path('jeux/<str:game>/', jeux_views.play_game, name='play_game'),
    path('jeux/record', jeux_views.record_score, name='record_score'),
    path('jeux/stats', jeux_views.stats, name='jeux_stats'),

    # Lobby pages
    path('lobby/<str:room_name>/', jeux_views.lobby_page, name='lobby'),  # added lobby URL with room_name
    path('get_open_lobbies/', jeux_views.get_open_lobbies, name='get_open_lobbies'),  # added get_open_lobbies URL
    path('create_lobby/', jeux_views.create_lobby, name='create_lobby'),  # added create_lobby URL
    path('play_lobby_game/<str:token>/', jeux_views.play_lobby_game, name='play_lobby_game'),  # added play_lobby_game URL
    
    # Paris
    path('paris/', paris_views.list_paris, name='list_paris'),
    path('paris/create', paris_views.create_pari, name='create_paris'),
    path('paris/<int:id>', paris_views.detail_pari, name='detail_pari'),
    path('parier/', paris_views.parier, name='parier'),
    path('conclure_pari/', paris_views.conclure, name='conclure_pari'),

    # Quêtes
    path('quêtes/', quests_views.quest, name='quest'),
    path('quêtes/achieved', quests_views.achieve_quest, name='achieve_quest'),
    path('quêtes/accept', quests_views.accept_quest, name='accept_quest'),

    # Atelier
    path('atelier/', atelier_views.atelier, name='atelier'),
    path('atelier/recycler', atelier_views.recycler, name='recycler'),

]