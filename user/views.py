from django.shortcuts import render, redirect
from .models import Follow
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your views here.
def my(request):
    """个人主页"""
    # my/?user_id=xxx
    user_id = request.GET.get('user_id', None)
    if not user_id:
        user_name = request.GET.get('user_name', None)
        if not user_name:
            user = request.user
        else:
            user = User.objects.get(username=user_name)
    else:
        user = User.objects.get(id=user_id)
    
    # 查看是否已经关注
    already_follow = Follow.objects.filter(followed=user, follower=request.user).exists()
    print(already_follow)

    print(user)
    return render(request, 'my.html', {'user': user, 'already_follow': already_follow})
    
def follow(request):
    user_id = request.GET.get('user_id')
    followed_user = User.objects.get(id=user_id)
    # 查看是否已经关注
    already_follow = Follow.objects.filter(followed=followed_user, follower=request.user).exists()
    if already_follow:
        raise ValueError("已经关注该用户")
    Follow.objects.create(follower=request.user, followed=followed_user)
    return redirect(request.META.get('HTTP_REFERER', '/'))  # 重载页面

def unfollow(request):
    user_id = request.GET.get('user_id')
    followed_user = User.objects.get(id=user_id)
    Follow.objects.filter(followed=followed_user, follower=request.user).delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))
    # return render(request, 'my.html', {'user': request.user})

def get_followers(request):
    user_id = request.GET.get('user_id')
    user = User.objects.get(id=user_id)
    if not user:
        return render(request, '404.html')

    followers = user.followers.all()
    return render(request, 'followers.html', {'followers': followers, 'user': user})


def get_followings(request):
    user_id = request.GET.get('user_id')
    user = User.objects.get(id=user_id)
    if not user:
        return render(request, '404.html')
    followings = user.following.all()
    return render(request, 'followings.html', {'followings': followings, 'user': user})


