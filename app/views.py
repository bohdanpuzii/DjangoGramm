import datetime
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, LoginByUsernameForm, EditProfile, PostPhoto, SearchForm
from .models import Profile, Photo, Subscriber, Like, Dislike
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, get_user, logout
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework.views import APIView

LOGIN_URL = '/signin/'


class FollowAPI(APIView):
    def post(self, request, who_to_follow_id):
        followed = True
        user = User.objects.get(id=who_to_follow_id)
        profile = Profile.objects.get(user=user)
        current_user = User.objects.get(id=request.user.id)
        current_profile = Profile.objects.get(user=current_user)
        if Subscriber.objects.filter(follower=current_profile, profile=profile):
            subscribe_to_delete = Subscriber.objects.get(follower=current_profile, profile=profile)
            subscribe_to_delete.delete()
            followed = False
        else:
            new_subscribe = Subscriber(follower=current_profile, profile=profile)
            new_subscribe.save()
        return Response({"followed": followed}, status=200)


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
        return Response({"likes_count": post.likes, "dislikes_count": post.unlikes}, status=200)


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
        return Response({"likes_count": post.likes, "dislikes_count": post.unlikes}, status=200)


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            psw = form.cleaned_data['psw']
            new_user = User(username=username, password=psw, email=email)
            new_user.set_password(form.cleaned_data['psw'])
            new_user.save()
            user = authenticate(request, username=username, password=psw)
            new_profile = Profile(user=user)
            new_profile.save()
            login(request, user)
            return redirect(edit_profile)
    else:
        form = RegisterForm()
    return render(request, "registration.html", {'form': RegisterForm})


def sign_in(request):
    if request.method == 'POST':
        form = LoginByUsernameForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            psw = form.cleaned_data['psw']
            user = authenticate(request, username=username, password=psw)
            if user is not None:
                login(request, user)
                return redirect(profile, id=user.id)
            else:
                return HttpResponse('Incorrect')
    else:
        form = LoginByUsernameForm()
    return render(request, "signin.html", {'form': LoginByUsernameForm})


@login_required(login_url=LOGIN_URL)
def profile(request, id):
    user = get_object_or_404(User, id=id)
    user_profile = Profile.objects.get(user=user)
    currents_user = User.objects.get(id=request.user.id)
    currents_user_profile = Profile.objects.get(user=currents_user)
    context = {'Profile': user_profile, 'user_id': request.user.id}
    if Photo.objects.filter(profile=Profile.objects.get(user=user)):
        context['Photo'] = Photo.objects.filter(profile=user_profile).order_by('-date')
    else:
        context['Photo'] = None
    if Subscriber.objects.filter(follower=currents_user_profile, profile=user_profile):
        context['followed'] = True
    else:
        context['followed'] = False
    if currents_user != user:
        context['able_to_follow'] = True
    else:
        context['able_to_follow'] = False
    return render(request, 'profile.html', context=context)


@login_required(login_url=LOGIN_URL)
def edit_profile(request):
    user = User.objects.get(id=request.user.id)
    user_profile = Profile.objects.get(user=user)
    if request.method == 'POST':
        form = EditProfile(request.POST, request.FILES)
        if form.is_valid():
            if form.cleaned_data['username']:
                user.username = form.cleaned_data['username']
            if form.cleaned_data['bio']:
                user_profile.bio = form.cleaned_data['bio']
            if form.cleaned_data['avatar']:
                user_profile.avatar = form.cleaned_data['avatar']
            user.save()
            user_profile.save()
            return redirect(profile, id=user.id)
    else:
        form = EditProfile()
    return render(request, "edit_profile.html", {'form': EditProfile})


@login_required(login_url=LOGIN_URL)
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


def logout_user(request):
    logout(request)
    return redirect(sign_in)


@login_required(login_url=LOGIN_URL)
def postphoto(request):
    user = get_user(request)
    current_profile = Profile.objects.get(user=user)
    text = ''
    if request.method == 'POST':
        form = PostPhoto(request.POST, request.FILES)
        if form.is_valid():
            if form.cleaned_data['photo']:
                photo = form.cleaned_data['photo']
                if form.cleaned_data['text']:
                    text = form.cleaned_data['text']
                new_post = Photo(photo=photo, text=text, profile=current_profile, date=datetime.datetime.now())
                new_post.save()
                return redirect(profile, id=user.id)
    else:
        form = PostPhoto()
    return render(request, 'post_photo.html', {'form': PostPhoto})


@login_required(login_url=LOGIN_URL)
def search(request):
    context = {'form': SearchForm}
    if request.method == 'GET':
        form = SearchForm(request.GET)
        if form.is_valid():
            searched_user = form.cleaned_data['searched_user']
            result_query = Profile.objects.filter(user__in=User.objects.filter(username__startswith=searched_user))
            context['profiles'] = result_query
    return render(request, 'search.html', context=context)
