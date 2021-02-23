from django import forms


class RegisterForm(forms.Form):
    email = forms.EmailField(label='Enter your email:')
    username = forms.CharField(label='Enter your username')
    psw = forms.CharField(widget=forms.PasswordInput, label='Your password')


class LoginByEmailForm(forms.Form):
    email = forms.EmailField(label='Enter your email')
    psw = forms.CharField(widget=forms.PasswordInput, label='Your password')


class LoginByUsernameForm(forms.Form):
    username = forms.CharField(label='Enter your username')
    psw = forms.CharField(widget=forms.PasswordInput, label='Your password')


class EditProfile(forms.Form):
    username = forms.CharField(label='New username', required=False)
    bio = forms.CharField(label='New info about you', required=False)
    avatar = forms.ImageField(label='New avatar', required=False)


class PostPhoto(forms.Form):
    photo = forms.ImageField(label='Choose photo')
    text = forms.CharField(label='Add description', required=False)


class SearchForm(forms.Form):
    searched_user = forms.CharField(label='')


