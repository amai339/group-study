from django.contrib import admin

# Register your models here.
from .models import Room,File
admin.site.register(Room)
admin.site.register(File)