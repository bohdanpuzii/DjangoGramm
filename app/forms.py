import datetime
from django import forms
from django.contrib.auth import authenticate
from .models import User, Profile, Photo


def create_user_and_profile(username, email, password):
    new_user = User(username=username, email=email)
    new_user.set_password(password)
    new_user.save()
    new_profile = Profile(user=new_user)
    new_profile.save()
    return new_user


def edit_profile_data(profile, new_username, new_bio, new_avatar):
    profile.bio = new_bio
    profile.avatar = new_avatar
    if not User.objects.filter(username=new_username) or profile.user.username == new_username:
        profile.user.username = new_username
        profile.user.save()
        profile.save()
        return True
    else:
        profile.save()
        profile.user.save()
        return False


def create_photo(profile, text, photo):
    new_photo = Photo(photo=photo, profile=profile, text=text, date=datetime.datetime.now())
    new_photo.save()
    return


class RegisterForm(forms.Form):
    email = forms.EmailField(label='Enter your email:')
    username = forms.CharField(label='Enter your username')
    password = forms.CharField(widget=forms.PasswordInput, label='Your password')

    def save(self, commit=True):
        email = self.cleaned_data['email']
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        return create_user_and_profile(username, email, password) if not User.objects.filter(
            username=username) else None


class SignInForm(forms.Form):
    username = forms.CharField(label='Enter your username')
    password = forms.CharField(widget=forms.PasswordInput, label='Your password')

    def save(self, commit=True):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        user = authenticate(username=username, password=password)
        return user


class EditProfileForm(forms.Form):
    username = forms.CharField(label='Username', required=False)
    bio = forms.CharField(label='Info about you', required=False)
    avatar = forms.ImageField(label='Avatar', required=False)

    def save(self, commit=True):
        profile = self.fields['profile']
        new_username = self.cleaned_data['username']
        new_bio = self.cleaned_data['bio']
        new_avatar = self.cleaned_data['avatar']
        return True if edit_profile_data(profile, new_username, new_bio, new_avatar) else False


class PostPhotoForm(forms.Form):
    photo = forms.ImageField(label='Choose photo')
    text = forms.CharField(label='Add description', required=False)

    def save(self, commit=True):
        profile = self.fields['profile']
        text = self.cleaned_data['text']
        photo = self.cleaned_data['photo']
        create_photo(profile, text, photo)
