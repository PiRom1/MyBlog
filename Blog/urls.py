from django.urls import path, include
from .views import chat_views, recits_views, lootbox_views, sondages_views, soundbox_views, tickets_views, user_views, utils_views, inventory_views, inventory_2_views, hdv_views, enjoy_timeline_views, jeux_views, paris_views, quests_views, dinowars_views, atelier_views, dinowars_pvm_views, journal_views

urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),

    path("", utils_views.getSession, name = "get_session"),
    path("get_sessions", utils_views.getSession_v2, name = "get_session_v2"),
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
    path('change_homepage_preference/', utils_views.change_homepage_preference, name='change_homepage_preference'),

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
    # path('lootbox/get', lootbox_views.get_lootbox, name='get_lootbox'),

    # Inventory
    path('inventory/', inventory_views.user_inventory_view, name='inventory'),
    path('inventory/toggle_item_favorite', inventory_views.toggle_item_favorite, name='toggle_item_favorite'),
    path('inventory/favorite', inventory_views.get_favorite_skins, name='get_favorite_skins'),
    path('inventory/update_equipped', inventory_views.update_equipped, name='update_equipped'),
    path('equip_bg', inventory_views.equip_bg, name='equip_bg'),
    path('unequip_bg', inventory_views.unequip_bg, name='unequip_bg'),
    path('unequip_dino_item', inventory_views.unequip_dino_item, name='unequip_dino_item'),

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
    path('hdv/remove_all', hdv_views.remove_all, name='remove_all'),
    path('hdv/get_market', hdv_views.get_market, name='get_market'),

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

    # DinoWars
    path('dinowars/', dinowars_views.user_dinos_view, name='user_dinos_view'),
    path('dinowars/edit_team/', dinowars_views.edit_team_view, name='edit_team_view'),
    path('dinowars/edit_team/<int:team_id>/', dinowars_views.edit_team_view, name='edit_team_view_with_id'),
    path('dinowars/delete_team/<int:team_id>/', dinowars_views.delete_team_view, name='delete_team_view'),
    path('dinowars/dino/<int:dino_id>/', dinowars_views.dino_details_view, name='dino_details_view'),
    path('dinowars/dino/<int:dino_id>/runes/', dinowars_views.dino_runes_view, name='dino_runes_view'),
    path('dinowars/remove_runes/', dinowars_views.remove_runes, name='remove_runes'),
    path('dinowars/inventory/runes/', dinowars_views.runes_inventory_view, name='runes_inventory_view'),
    path('dinowars/dino/<int:dino_id>/equip-rune/', dinowars_views.equip_rune, name='equip_rune'),
    path('dinowars/fuse-dinos/', dinowars_views.fuse_dinos, name='fuse_dinos'),
    path('dinowars/hatch/', dinowars_views.hatch_dino, name='hatch_dino'),
    path('dinowars/battle/', dinowars_views.battle_view, name='battle_view'),
    path('dinowars/arena/', dinowars_views.arena_view, name='arena_view'),
    path('dinowars/start_battle/', dinowars_views.start_battle, name='start_battle'),
    path('dinowars/battle/analytics/<int:fight_id>/', dinowars_views.battle_analytics_view, name='battle_analytics_view'),
    path('dinowars/get_dino_nb_to_evolve/<int:dino_id>/', dinowars_views.get_dino_nb_to_evolve, name="get_dino_nb_to_evolve"),
    path('dinowars/pvm/', dinowars_pvm_views.pvm_view, name='pvm_view'),
    path('dinowars/pvm/dino/<int:dino_id>/', dinowars_pvm_views.run_dino_details_view, name='run_dino_details_view'), 
    path('dinowars/pvm/dino/<int:dino_id>/level-up/', dinowars_pvm_views.stat_allocation_view, name='pvm_dino_level_up'),
    path('dinowars/pvm/dino/<int:dino_id>/level-up/<str:stat_name>/', dinowars_pvm_views.level_up_stat_view, name='pvm_dino_level_up_stat'),
    path('dinowars/pvm/ability/<int:ability_id>/select/', dinowars_pvm_views.select_ability_view, name='select_ability'),
    path('dinowars/pvm/ability/<int:ability_id>/select-dino/', dinowars_pvm_views.select_ability_dino_view, name='select_ability_dino'),
    path('dinowars/pvm/new-run/', dinowars_pvm_views.new_run_view, name='new_run_view'),
    path('dinowars/pvm/select-run-dino/', dinowars_pvm_views.select_run_dino_view, name='select_run_dino_view'),
    path('dinowars/pvm/start_battle/', dinowars_pvm_views.start_battle_pvm, name='start_battle_pvm'),
    path('dinowars/pvm/run-fights/', dinowars_pvm_views.get_run_fights_view, name='get_run_fights_view'),
    path('dinowars/leaderboard/', dinowars_pvm_views.leaderboard_view, name='leaderboard_view'),

    # Atelier
    path('atelier/', atelier_views.atelier, name='atelier'),
    path('atelier/recycler', atelier_views.recycler, name='recycler'),

    # Journal
    path('get_journal_entries/', journal_views.get_journal_entries, name='get_journal_entries'),
    path('get_notifications_number/', journal_views.get_notifications_number, name='get_notifications_number'),
    path('manage_notification_entry/', journal_views.manage_notification_entry, name='manage_notification_entry'),
    

]