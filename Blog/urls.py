from django.urls import path, include

from . import views

urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),

    path("", views.getSession, name = "get_session"),
    path("<int:id>/", views.Index, name="index"),
    path("login/", views.connexion, name = "login"),
    path("logout/", views.deconnexion, name = "logout"),
    path("invalid_user/", views.InvalidUser, name = "invalid_user"),
    #path("dark_mode/", views.dark_mode, name = "dark_mode")
    # path("add_user/", views.AddUser, name = "add_user"),
    #path("upvote/<int:message_id>/", views.upvote, name = "upvote"),
    #path("downvote/<int:message_id>/", views.downvote, name = "downvote"),
    # path("modify/<int:message_id>/", views.Modify, name = "modify"),

    # TICKETS #
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/create/', views.create_ticket, name='create_ticket'),
    path('tickets/update/<int:pk>/', views.update_ticket, name='update_ticket'),
    path('change_photo', views.change_photo, name = 'change_photo'),
]