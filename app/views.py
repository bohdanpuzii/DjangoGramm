from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth import login, logout
from django.views.generic.edit import FormView, View
from rest_framework.response import Response
from rest_framework.views import APIView
from .forms import RegisterForm, SignInForm, PostPhotoForm, EditProfileForm
from .models import Profile, Photo, Subscriber, Like, Dislike


class Registration(FormView):
    template_name = 'registration.html'
    form_class = RegisterForm
    success_url = reverse_lazy('edit_profile')

    def form_valid(self, form):
        profile = form.save()
        login(self.request, profile,
              backend='django.contrib.auth.backends.ModelBackend') if profile is not None else messages.warning(
            self.request, 'This username is already used')
        return super().form_valid(form)


class SignIn(FormView):
    template_name = 'signin.html'
    form_class = SignInForm

    def form_valid(self, form):
        user = form.save()
        login(self.request, user) if user is not None else messages.warning(self.request,
                                                                            'Incorrect password or login')
        return super().form_valid(form)

    def get_success_url(self):
        profile = self.request.user
        return reverse('profile', args=[profile.id]) if profile.is_authenticated else reverse('signin')


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
        if not form.save():
            messages.warning(self.request, 'Username is already used')
        return super().form_valid(form)

    def get_success_url(self):
        profile_id = self.request.user.id
        return reverse('profile', args=[profile_id])


class UserProfile(View):
    def get(self, request, profile_id):
        current_profile = request.user
        visited_profile = get_object_or_404(Profile, id=profile_id)
        context = {'Profile': visited_profile, 'user_id': request.user.id,
                   'Photo': Photo.objects.filter(profile=visited_profile).order_by('-date'),
                   'followed': bool(Subscriber.objects.filter(follower=current_profile,
                                                              profile=visited_profile)),
                   'able_to_follow': not current_profile == visited_profile}
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

    def get_success_url(self):
        profile_id = self.request.user.id
        return reverse('profile', args=[profile_id])


class FollowAPI(APIView):
    def post(self, request, who_to_follow_id):
        followed_profile = Profile.objects.get(id=who_to_follow_id)
        current_profile = request.user
        subscription_exists = Subscriber.objects.filter(follower=current_profile, profile=followed_profile)
        followed = delete_subscription(current_profile,
                                       followed_profile) if subscription_exists else create_subscription(
            current_profile, followed_profile)
        return Response({"followed": followed}, status=201)


def delete_subscription(current_profile, followed_profile):
    subscribe_to_delete = Subscriber.objects.get(follower=current_profile, profile=followed_profile)
    subscribe_to_delete.delete()
    return False


def create_subscription(current_profile, followed_profile):
    new_subscribe = Subscriber(follower=current_profile, profile=followed_profile)
    new_subscribe.save()
    return True


class LikeAPI(APIView):
    def post(self, request, post_id):
        current_profile = request.user
        post = Photo.objects.get(id=post_id)
        like_exists = Like.objects.filter(who_liked=current_profile, post=post)
        dislike_exists = Dislike.objects.filter(who_disliked=current_profile, post=post)
        if not like_exists and dislike_exists:
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
        dislike_exists = Dislike.objects.filter(who_disliked=current_profile, post=post)
        like_exists = Like.objects.filter(who_liked=current_profile, post=post)
        if not dislike_exists and like_exists:
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


class Search(View):
    def get(self, searched_string):
        searched_string = self.request.GET.get("searched_string")
        context = {'Profiles': Profile.objects.filter(username__contains=searched_string),
                   'Photos': Photo.objects.filter(text__contains=searched_string)}
        return render(self.request, 'search.html', context)
