from django.urls import path

from . import views

urlpatterns = [
    path("import", views.import_photos, name="import"),
    path("import_2", views.import_photos_2, name="import_2"),
    path("convert", views.convert, name="convert"),
    path("convert_2", views.convert_2, name="convert_2"),
    path("download", views.download_zip, name="download"),
]