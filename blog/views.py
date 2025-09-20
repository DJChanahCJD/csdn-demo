from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, reverse
from django.core.mail import send_mail
from django.core.cache import cache
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth import get_user_model, login, logout
from .forms import RegisterForm, LoginForm, PostForm
from .models import Category, Blog, Comment, UserProfile
from common.cache import CacheKey, redis_client
import random
from .tasks import send_email_captcha_task
import time

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

User = get_user_model()

# Create your views here.
def index(request):
    params = {
        'category_id': request.GET.get('category_id'),
        'user_id': request.GET.get('user_id')
    }
    categories = Category.objects.all()

    # 构建基础查询集
    blogs = Blog.objects.select_related('author', 'category')

    # 应用过滤条件
    if params['category_id']:
        blogs = blogs.filter(category_id=params['category_id'])

    if params['user_id']:
        blogs = blogs.filter(author_id=params['user_id'])

    context = {
        'blogs': blogs,
        'current_category_id': params['category_id'],
        'categories': categories
    }

    return render(request, 'index.html', context)

def search_blog(request):
    query = request.GET.get('q')
    # 获取标题和内容包含q的博客
    blogs = Blog.objects.filter(Q(title__icontains=query) | Q(content__icontains=query))
    return render(request, 'index.html', {'blogs': blogs})

def page_not_found(request, exception=None):
    return render(request, '404.html', status=404)

def blog_detail(request, blog_id):
    try:
        blog = Blog.objects.get(id=blog_id)
        return render(request, 'blog_detail.html', {'blog': blog})
    except Blog.DoesNotExist:
        return render(request, '404.html')


@login_required()  # 在settings.py中配置了LOGIN_URL
@require_http_methods(['GET', 'POST'])
def pub_blog(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        return render(request, 'pub_blog.html', {'categories': categories})
    else:
        form = PostForm(request.POST)
        if not form.is_valid():
            print(form.errors)
            return JsonResponse({'code': 400, 'msg': '发布失败'})
        title = form.cleaned_data['title']
        category_id = form.cleaned_data['category']
        content = form.cleaned_data['content']
        blog = Blog.objects.create(title=title, category_id=category_id, content=content, author=request.user)
        # 考虑到平台大博主较少，采用推送的模式, 存入对应userid的zset中, 分数为时间

        # 1. 先获取所有关注该博主的用户
        follows = request.user.followers.all()
        # 2. 给所有关注该博主的用户发送消息
        for follow in follows:
            # 3. 发送消息
            redis_client.zadd(CacheKey.BLOG_FEED % follow.follower.id, {blog.id: time.time()})
            
            # 添加实时推送功能
            channel_layer = get_channel_layer()
            # 构造推送数据
            blog_data = {
                'id': blog.id,
                'title': blog.title,
                'content': blog.content,
                'author': {
                    'id': blog.author.id,
                    'username': blog.author.username,
                    'avatarUrl': blog.author.profile.avatarUrl
                },
                'pub_time': blog.pub_time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 发送到用户特定的组
            async_to_sync(channel_layer.group_send)(
                f"message_{follow.follower.id}",
                {
                    'type': 'message.update',
                    'data': blog_data
                }
            )
        return JsonResponse({'code': 200, 'msg': '发布成功', 'data': {'blog_id': blog.id}})

def message(request):
    user = request.user
    # 1. 先获取用户的博客流
    blog_ids = redis_client.zrevrange(CacheKey.BLOG_FEED % user.id, 0, -1)
    # 2. 根据博客id获取博客详情
    blogs = Blog.objects.filter(id__in=blog_ids).select_related('author', 'category')
    return render(request, 'message.html', {'blogs': blogs})

@require_POST
@login_required()  # 在settings.py中配置了LOGIN_URL
def pub_comment(request):
    blog_id = request.POST.get('blog_id')
    content = request.POST.get('content')
    Comment.objects.create(blog_id=blog_id, content=content, author=request.user)
    # 重新加载详情页面
    return redirect(reverse('blog:blog_detail', kwargs={'blog_id': blog_id}))

@require_http_methods(['GET', 'POST'])
def csdn_login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        form = LoginForm(request.POST)
        if not form.is_valid():
            print(form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}:{error}')
            return render(request, 'login.html', {'form': form})
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        remember = form.cleaned_data['remember']
        user = User.objects.get(email=email)
        if not user or not user.check_password(password):
            messages.error(request, '邮箱或密码错误')
            return render(request, 'login.html', {'form': form})
        # 注册成功后，跳转到首页
        login(request, user)
        print("登录后:", request.user)

        if not remember:
            request.session.set_expiry(0)  # 不保持登录状态，则sessionId只在会话期有效
        messages.success(request, '登录成功')
        return redirect('/')


@require_http_methods(['GET', 'POST'])
def csdn_register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    else:
        form = RegisterForm(request.POST)
        if not form.is_valid():
            print(form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
            return render(request, 'register.html', {'form': form})
        email = form.cleaned_data['email']
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = User.objects.create_user(username=username, email=email, password=password)
        # 注册成功后，创建用户Profile, 并设置默认头像
        UserProfile.objects.create(user=user, avatarUrl=f'https://api.dicebear.com/9.x/avataaars/svg?seed={user.username}')
        # 注册成功后，跳转到登录页
        messages.success(request, '注册成功')
        return redirect(reverse('blog:login'))


def csdn_logout(request):
    logout(request)
    messages.success(request, '退出登录')
    return redirect('/')


def send_email_captcha(request):
    # ?email=xxx
    email = request.GET.get('email')
    if not email:
        return JsonResponse({'code': 400, 'msg': '邮箱不能为空'})
    # # 检查是否已存在未过期的验证码
    # existing_captcha = cache.get(CacheKey.EMAIL_CAPTCHA % email)
    # if existing_captcha:
    #     return JsonResponse({'code': 400, 'msg': '验证码已发送，请稍后再试'})
    # 发送验证码（随机6位数字）, 存储String类型
    captcha = random.sample('0123456789', 6)
    captcha = ''.join(captcha)
    print(email, captcha)
    # 将验证码存储到redis中, 并设置过期时间为5分钟
    cache.set(CacheKey.EMAIL_CAPTCHA % email, captcha, 60 * 5)
    # 异步发送邮件
    send_email_captcha_task.delay(
        subject='验证码 - CSDN',
        message=f'您的验证码是：{captcha}',
        recipient_email=email
    )
    return JsonResponse({'code': 200, 'msg': '验证码发送成功'})
