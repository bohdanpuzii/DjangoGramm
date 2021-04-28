from django.contrib import admin
from .models import Profile, Photo, Like, Dislike, Subscriber

admin.site.register(Profile)
admin.site.register(Photo)
admin.site.register(Like)
admin.site.register(Dislike)
admin.site.register(Subscriber)
