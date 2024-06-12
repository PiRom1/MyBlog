from django.urls import path

from . import views

urlpatterns = [
    path("", views.Index, name="index"),
    path("add_user/", views.AddUser, name = "add_user"),
    path("connexion/", views.connexion, name = "connexion")
]