from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, SignInForm, PostPhotoForm, EditProfileForm
from .models import Profile, Photo, Subscriber, Like, Dislike
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, get_user, logout
from django.views.generic.edit import FormView, View
from rest_framework.response import Response
from rest_framework.views import APIView


class Registration(FormView):
    template_name = 'registration.html'
    form_class = RegisterForm

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect(reverse('edit_profile'))
        else:
            messages.warning(self.request, 'This username is already used')
            return redirect(reverse('register'))


class SignIn(FormView):
    template_name = 'signin.html'
    form_class = SignInForm

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
            return redirect(reverse('profile', args=[self.request.user.id]))
        else:
            messages.warning(self.request, 'Incorrect password or login')
            return redirect(reverse('signin'))


class EditProfile(FormView):
    template_name = 'edit_profile.html'
    form_class = EditProfileForm

    def get_initial(self):
        user_profile = Profile.objects.get(user=self.request.user)
        profile_data = {'username': self.request.user.username, 'bio': user_profile.bio, 'avatar': user_profile.avatar}
        return profile_data

    def form_valid(self, form):
        form.fields['profile'] = Profile.objects.get(user=self.request.user)
        if form.save():
            return redirect(reverse('profile', args=[self.request.user.id]))
        else:
            messages.warning(self.request, 'Username is already used')
            return redirect(reverse('edit_profile'))


class UserProfile(View):
    def get(self, request, user_id):
        current_user_profile = Profile.objects.get(user=request.user)
        user = get_object_or_404(User, id=user_id)
        user_profile = Profile.objects.get(user=user)
        context = {'Profile': user_profile, 'user_id': request.user.id,
                   'Photo': Photo.objects.filter(profile=user_profile).order_by('-date'),
                   'followed': True if Subscriber.objects.filter(follower=current_user_profile,
                                                                 profile=user_profile) else False,
                   'able_to_follow': False if current_user_profile == user_profile else True}
        return render(request, 'profile.html', context=context)


def feed(request):
    if Profile.objects.filter(user=request.user):
        current_profile = Profile.objects.get(user=request.user)
    else:
        current_profile = Profile(user=request.user)
        current_profile.save()
        request.user.save()
    subscribers = Subscriber.objects.filter(follower=current_profile).values('profile')
    context = {'Photos': Photo.objects.filter(profile__in=subscribers).order_by('date')}
    return render(request, 'feed.html', context=context)


class Logout(View):
    def get(self, request):
        logout(request)
        return redirect(reverse('signin'))


class PostPhoto(FormView):
    template_name = 'post_photo.html'
    form_class = PostPhotoForm

    def form_valid(self, form):
        form.fields['profile'] = Profile.objects.get(user=self.request.user)
        return redirect(reverse('profile', args=[self.request.user.id]))


class FollowAPI(APIView):
    def post(self, request, who_to_follow_id):
        followed = True
        user = User.objects.get(id=who_to_follow_id)
        profile = Profile.objects.get(user=user)
        current_profile = Profile.objects.get(user=request.user)
        if Subscriber.objects.filter(follower=current_profile, profile=profile):
            subscribe_to_delete = Subscriber.objects.get(follower=current_profile, profile=profile)
            subscribe_to_delete.delete()
            followed = False
        else:
            new_subscribe = Subscriber(follower=current_profile, profile=profile)
            new_subscribe.save()
        return Response({"followed": followed}, status=201)


class LikeAPI(APIView):
    def post(self, request, post_id):
        current_user = User.objects.get(id=request.user.id)
        current_profile = Profile.objects.get(user=current_user)
        post = Photo.objects.get(id=post_id)
        if not Like.objects.filter(who_liked=current_profile, post=post):
            if Dislike.objects.filter(who_disliked=current_profile, post=post):
                dislike_to_delete = Dislike.objects.filter(who_disliked=current_profile, post=post)
                dislike_to_delete.delete()
                post.unlikes -= 1
                post.save()
            like = Like(who_liked=current_profile, post=post)
            like.save()
            post.likes += 1
            post.save()
        return Response({"likes_count": post.likes, "dislikes_count": post.unlikes}, status=201)


class DislikeAPI(APIView):
    def post(self, request, post_id):
        current_user = User.objects.get(id=request.user.id)
        current_profile = Profile.objects.get(user=current_user)
        post = Photo.objects.get(id=post_id)
        if not Dislike.objects.filter(who_disliked=current_profile, post=post):
            if Like.objects.filter(who_liked=current_profile, post=post):
                like_to_delete = Like.objects.filter(who_liked=current_profile, post=post)
                like_to_delete.delete()
                post.likes -= 1
                post.save()
            dislike = Dislike(who_disliked=current_profile, post=post)
            dislike.save()
            post.unlikes += 1
            post.save()
        return Response({"likes_count": post.likes, "dislikes_count": post.unlikes}, status=201)
