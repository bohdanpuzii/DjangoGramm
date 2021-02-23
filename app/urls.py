from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.register, name='register'),
    path('signin/', views.sign_in, name='signin'),
    path('edit_profile/', views.edit_profile, name='editprofile'),
    path('profile/<int:id>', views.profile, name='profile'),
    path('logout', views.logout_user, name='logout'),
    path('post_photo/', views.postphoto, name='postphoto'),
    path('feed/', views.feed, name='feed'),
    path('like/<int:post_id>', views.LikeAPI.as_view(), name='like'),
    path('unlike/<int:post_id>', views.DislikeAPI.as_view(), name='unlike'),
    path('follow/<int:who_to_follow_id>', views.FollowAPI.as_view(), name='follow'),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('search/', views.search, name='search')
]
