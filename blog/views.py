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
from common.cache import cacheKey
import random

User = get_user_model()

# Create your views here.
def index(request):
    blogs = Blog.objects.all()
    return render(request, 'index.html', {'blogs': blogs})

def search_blog(request):
    query = request.GET.get('q')
    # 获取标题和内容包含q的博客
    blogs = Blog.objects.filter(Q(title__icontains=query) | Q(content__icontains=query))
    return render(request, 'index.html', {'blogs': blogs})

def page_not_found(request):
    return render(request, '404.html')

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
        return JsonResponse({'code': 200, 'msg': '发布成功', 'data': {'blog_id': blog.id}})


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
    # 发送验证码（随机6位数字）, 存储String类型
    captcha = random.sample('0123456789', 6)
    captcha = ''.join(captcha)
    # 将验证码存储到redis中, 并设置过期时间为5分钟
    cache.set(cacheKey.EMAIL_CAPTCHA % email, captcha, 60 * 5)
    # 发送邮件
    send_mail(
        subject='验证码 - CSDN',
        message=f'您的验证码是：{captcha}',
        from_email=None,  # 将使用settings.py中的DEFAULT_FROM_EMAIL
        recipient_list=[email],
        fail_silently=False,
    )
    return JsonResponse({'code': 200, 'msg': '验证码发送成功'})


def verify_email_captcha(email, captcha):
    # ?email=xxx&captcha=xxx
    if not email or not captcha:
        return JsonResponse({'code': 400, 'msg': '邮箱或验证码不能为空'})
    # 从redis中获取验证码
    cache_captcha = cache.get(cacheKey.EMAIL_CAPTCHA % email)  # 默认存储在version=1, 即csdn:1:email_captcha
    if not cache_captcha:
        return JsonResponse({'code': 400, 'msg': '验证码过期'})
    if cache_captcha != captcha:
        return JsonResponse({'code': 400, 'msg': '验证码错误'})
    return JsonResponse({'code': 200, 'msg': '验证码校验成功'})
