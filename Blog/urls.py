from django.urls import path, include

from . import views

urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),

    path("", views.getSession, name = "get_session"),
    path("<int:id>/", views.Index, name="index"),
    path("login/", views.connexion, name = "login"),
    path("logout/", views.deconnexion, name = "logout"),
    path("invalid_user/", views.InvalidUser, name = "invalid_user"),
    path("stats/<int:id>/", views.Stats, name="stats"),
    path("user/<int:id>/", views.UserView, name="user"),
    path("user/<int:id>/messages", views.IndexUser, name="index_user"),
    path("user/<int:id>/messages/<str:word>", views.IndexUserMessage, name="index_user_message"),
    path('change_photo', views.change_photo, name = 'change_photo'),
    #path("dark_mode/", views.dark_mode, name = "dark_mode")
    # path("add_user/", views.AddUser, name = "add_user"),
    # path("upvote/<int:message_id>/", views.upvote, name = "upvote"),
    # path("downvote/<int:message_id>/", views.downvote, name = "downvote"),
    # path("modify/<int:message_id>/", views.Modify, name = "modify"),

    # TICKETS #
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/create/', views.create_ticket, name='create_ticket'),
    path('tickets/update/<int:pk>/', views.update_ticket, name='update_ticket'),
   

    # SONDAGES #
    path('sondages/', views.sondage_list, name='sondage_list'),
    path('sondages/create/', views.create_sondage, name='create_sondage'),
    path('sondages/update/<int:pk>/', views.update_sondage, name='update_sondage'),
    path('sondages/delete/<int:pk>/', views.delete_sondage, name='delete_sondage'),
    path('sondages/detail/<int:pk>/', views.detail_sondage, name='detail_sondage'),
    path('sondages/vote/<int:sondage_id>/<int:choice_id>/', views.vote_sondage, name = 'vote_sondage'),

    # Récits
    path('recits/', views.recit_list, name='recit_list'),
    path('recits/create/', views.create_recit, name='create_recit'),
    path('recits/detail/<int:pk>/', views.detail_recit, name='detail_recit'),

    # Lootbox
    path('lootbox/open', views.open_lootbox, name='open_lootbox'),  

    # Soundbox
    path('list_sounds', views.list_sounds, name='list_sounds'),
    path('add_sounds', views.add_sounds, name='add_sounds'),

    # Other
    path('increment_yoda/', views.increment_yoda, name='increment_yoda'),
    path('increment_enjoy/', views.increment_enjoy, name='increment_enjoy'),
    path('increment_sound/', views.increment_sound, name='increment_sound'),
    path('tkt/', views.tkt_view, name='tkt'),
    path('update_plot/', views.update_plot, name='update_plot'),
    path('update_soundbox/', views.update_soundbox, name='update_soundbox'),
    
]