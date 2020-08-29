from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.
class Room(models.Model):
    name = models.CharField("Room name",max_length=100)
    description = models.CharField("Room description",max_length=1000)
    private = models.BooleanField()
    users = models.ManyToManyField(User)
    invited = models.ManyToManyField(User,related_name = 'invited')
    admin = models.ManyToManyField(User,related_name = 'admin')

    def __str__(self):
        return self.name + '\n' +self.description +'\n'+ ('Public' if self.private == False else 'Private')


class File(models.Model):
    name = models.CharField('File name',max_length=200)
    file = models.FilePathField(path=settings.MEDIA_ROOT)
    room = models.ForeignKey(Room,on_delete=models.CASCADE)

    def __str__(self):
        return self.file