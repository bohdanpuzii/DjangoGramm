from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = CloudinaryField('avatar')
    bio = models.CharField(max_length=100)


class Photo(models.Model):
    photo = CloudinaryField('photo')
    text = models.CharField(max_length=100)
    date = models.DateTimeField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, default=None)
    likes = models.IntegerField(default=0)
    unlikes = models.IntegerField(default=0)


class Subscriber(models.Model):
    follower = models.ForeignKey(Profile, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='profile_to_be_subscribed')


class Like(models.Model):
    who_liked = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Photo, on_delete=models.CASCADE, default=None)


class Dislike(models.Model):
    who_disliked = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Photo, on_delete=models.CASCADE, default=None)
