from django.db import models

# Create your models here.


class Photo(models.Model):
    file = models.FileField(upload_to = "images/cr2")
    new = models.BooleanField(default = True)

    def __str__(self):
        return(str(self.file).split('/')[-1])


class PhotoSet(models.Model):

    text = models.TextField(blank=False, max_length = 500)


class PhotoFile(models.Model):
    file = models.FileField(upload_to="images/cr2")
    set = models.ForeignKey(PhotoSet, on_delete=models.CASCADE)


