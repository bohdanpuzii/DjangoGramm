from django.test import TestCase, Client
from .models import Profile, Photo, User, Like, Dislike, Subscriber
from datetime import datetime
from django.urls import reverse


class ModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user')
        self.user2 = User.objects.create_user(username='test2')
        self.profile = Profile.objects.create(user=self.user, bio='hello, im test', avatar=None)
        self.profile2 = Profile.objects.create(user=self.user2, bio='', avatar=None)
        self.photo = Photo.objects.create(profile=self.profile, text='Hello world!', photo=None, date=datetime.now())
        self.subscriber = Subscriber.objects.create(follower=self.profile, profile=self.profile2)
        self.like = Like.objects.create(who_liked=self.profile, post=self.photo)
        self.dislike = Dislike.objects.create(who_disliked=self.profile, post=self.photo)

    def test_user_test(self):
        profile = ''
        user = User.objects.filter(username='test_user')
        for i in user:
            self.assertEqual(i.username, 'test_user')
            profile = Profile.objects.filter(user=i)
        for i in profile:
            self.assertEqual(i.bio, 'hello, im test')
            photo = Photo.objects.filter(profile=i)
        for i in photo:
            self.assertEqual(i.text, 'Hello world!')
        user = User.objects.filter(username='not_test_user')
        for i in user:
            self.assertEqual(i, None)
        profile = Profile.objects.filter(bio='not_test_user')
        for i in profile:
            self.assertEqual(i, None)
        photo = Photo.objects.filter(text='not_test_user')
        for i in photo:
            self.assertEqual(i, None)
        subscriber = Subscriber.objects.filter(follower=self.profile, profile=self.profile2)
        for i in subscriber:
            self.assertEqual(i.follower.user.username, 'test_user')
            self.assertEqual(i.profile.user.username, 'test2')
        like = Like.objects.filter(who_liked=self.profile, post=self.photo)
        for i in like:
            self.assertEqual(i.who_liked.bio, 'hello, im test')
            self.assertEqual(like.count(), 1)
        dislike = Dislike.objects.filter(who_disliked=self.profile, post=self.photo)
        for i in dislike:
            self.assertEqual(i.who_disliked.bio, 'hello, im test')
            self.assertEqual(dislike.count(), 1)


class TestViews(TestCase):
    def test_views_get(self):
        client = Client()
        response = client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration.html')
        response = client.get(reverse('signin'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signin.html')

    def test_views_post(self):
        client = Client()
        response = client.post(reverse('register'),
                               {'email': 'bogdan.puziy@gmail.com', 'username': 'chiper', 'psw': '12345678abcde'})
        self.assertEqual(response.status_code, 302)
        response = client.post(reverse('register'),
                               {'email': 'bogdan.puzii@gmail.com', 'username': 'chiper1', 'psw': '12345678abcde'})
        self.assertEqual(response.status_code, 302)
        response = client.post(reverse('signin'),
                               {'username': 'chiper', 'psw': '12345678abcde'})
        current_user = User.objects.get(username='chiper')
        current_profile = Profile.objects.get(user=current_user)
        self.assertEqual(response.status_code, 302)
        response = client.post(reverse('postphoto'), {'photo': '', 'text': 'Hello world'})
        posted_photo = Photo.objects.filter(text='Hello world')
        self.assertEqual(response.status_code, 200)
        for i in posted_photo:
            response = client.post(reverse('like', args=[i.id]))
            self.assertEqual(response.status_code, 200)
            response = client.post(reverse('unlike', args=[i.id]))
            self.assertEqual(response.status_code, 200)
        user_to_follow = User.objects.get(username='chiper1')
        profile_to_follow = Profile.objects.get(user=user_to_follow)
        response = client.post(reverse('follow', args=[profile_to_follow.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Subscriber.objects.filter(profile=profile_to_follow, follower=current_profile).exists())
        response = client.post(reverse('follow', args=[profile_to_follow.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Subscriber.objects.filter(profile=profile_to_follow, follower=current_profile).exists())
