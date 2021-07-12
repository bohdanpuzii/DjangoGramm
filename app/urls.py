from django.urls import path, include
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('', views.Registration.as_view(), name='register'),
    path('sign_in/', views.SignIn.as_view(), name='signin'),
    path('edit_profile/', login_required(views.EditProfile.as_view()), name='edit_profile'),
    path('profile/<int:profile_id>', login_required(views.UserProfile.as_view()), name='profile'),
    path('logout', login_required(views.Logout.as_view()), name='logout'),
    path('post_photo/', login_required(views.PostPhoto.as_view()), name='postphoto'),
    path('feed/', login_required(views.Feed.as_view()), name='feed'),
    path('like/<int:post_id>', views.LikeAPI.as_view(), name='like'),
    path('unlike/<int:post_id>', views.DislikeAPI.as_view(), name='unlike'),
    path('follow/<int:who_to_follow_id>', views.FollowAPI.as_view(), name='follow'),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('search/', views.Search.as_view(), name='search')
]
