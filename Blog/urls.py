from django.urls import path, include

from . import views

urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),

    path("", views.getSession, name = "get_session"),
    path("<int:id>/", views.Index, name="index"),
    # path("add_user/", views.AddUser, name = "add_user"),
    path("login/", views.connexion, name = "login"),
    #path("upvote/<int:message_id>/", views.upvote, name = "upvote"),
    #path("downvote/<int:message_id>/", views.downvote, name = "downvote"),
    # path("modify/<int:message_id>/", views.Modify, name = "modify"),
    path("logout/", views.deconnexion, name = "logout"),
    path("invalid_user/", views.InvalidUser, name = "invalid_user"),
    #path("dark_mode/", views.dark_mode, name = "dark_mode")
]