from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, SignInForm, PostPhotoForm, EditProfileForm
from .models import Profile, Photo, Subscriber, Like, Dislike
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, logout
from django.views.generic.edit import FormView, View
from rest_framework.response import Response
from rest_framework.views import APIView


class Registration(FormView):
    template_name = 'registration.html'
    form_class = RegisterForm

    def form_valid(self, form):
        profile = form.save()
        if profile is not None:
            login(self.request, profile, backend='django.contrib.auth.backends.ModelBackend')
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
        profile = self.request.user
        profile_data = {'username': profile.username, 'bio': profile.bio,
                        'avatar': profile.avatar}
        return profile_data

    def form_valid(self, form):
        profile = self.request.user
        form.fields['profile'] = profile
        if form.save():
            return redirect(reverse('profile', args=[profile.id]))
        else:
            messages.warning(self.request, 'Username is already used')
            return redirect(reverse('edit_profile'))


class UserProfile(View):
    def get(self, request, profile_id):
        current_profile = request.user
        page_profile = get_object_or_404(Profile, id=profile_id)
        context = {'Profile': page_profile, 'user_id': request.user.id,
                   'Photo': Photo.objects.filter(profile=page_profile).order_by('-date'),
                   'followed': True if Subscriber.objects.filter(follower=current_profile,
                                                                 profile=page_profile) else False,
                   'able_to_follow': False if current_profile == page_profile else True}
        return render(request, 'profile.html', context=context)


class Feed(View):
    def get(self, request):
        current_profile = request.user
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
        form.fields['profile'] = self.request.user
        form.save()
        return redirect(reverse('profile', args=[self.request.user.id]))


class FollowAPI(APIView):
    def post(self, request, who_to_follow_id):
        followed = True
        profile = Profile.objects.get(id=who_to_follow_id)
        current_profile = request.user
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
        current_profile = request.user
        post = Photo.objects.get(id=post_id)
        if not Like.objects.filter(who_liked=current_profile, post=post) and Dislike.objects.filter(
                who_disliked=current_profile, post=post):
            delete_dislike(current_profile, post)
        create_like(current_profile, post)
        return Response({"likes_count": post.likes, "dislikes_count": post.unlikes}, status=201)


def create_like(profile, post):
    like = Like(who_liked=profile, post=post)
    like.save()
    post.likes += 1
    post.save()


def delete_dislike(profile, post):
    dislike_to_delete = Dislike.objects.filter(who_disliked=profile, post=post)
    dislike_to_delete.delete()
    post.unlikes -= 1
    post.save()


class DislikeAPI(APIView):
    def post(self, request, post_id):
        current_profile = request.user
        post = Photo.objects.get(id=post_id)
        if not Dislike.objects.filter(who_disliked=current_profile, post=post):
            if Like.objects.filter(who_liked=current_profile, post=post):
                delete_like(current_profile, post)
            create_dislike(current_profile, post)
        return Response({"likes_count": post.likes, "dislikes_count": post.unlikes}, status=201)


def delete_like(profile, post):
    like_to_delete = Like.objects.filter(who_liked=profile, post=post)
    like_to_delete.delete()
    post.likes -= 1
    post.save()


def create_dislike(profile, post):
    dislike = Dislike(who_disliked=profile, post=post)
    dislike.save()
    post.unlikes += 1
    post.save()
