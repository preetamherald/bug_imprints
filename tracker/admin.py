from django.contrib import admin
from .models import *

# Register your models here.

#register all models to admin
admin.site.register(Teams)
admin.site.register(MediaStore)
admin.site.register(Messeges)
admin.site.register(Bug)
admin.site.register(BugResolution)
admin.site.register(BugWatch)
admin.site.register(BugDuplicate)



