from django.urls import path

from . import views
app_name = 'user'
urlpatterns = [
    path('my', views.my, name='my'),
    path('follow', views.follow, name='follow'),
    path('unfollow', views.unfollow, name='unfollow'),
    path('get_followers', views.get_followers, name='get_followers'),
    path('get_followings', views.get_followings, name='get_followings'),
]
