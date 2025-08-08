from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from common.cache import cacheKey

User = get_user_model()

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=20, min_length=3, required=True, error_messages={})
    email = forms.EmailField(required=True, error_messages={})
    captcha = forms.CharField(max_length=6, min_length=6, required=True, error_messages={})
    password = forms.CharField(max_length=20, min_length=3, required=True, error_messages={})

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('该用户名已存在')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已存在')
        return email

    def clean_captcha(self):
        captcha = self.cleaned_data.get('captcha')
        email = self.cleaned_data.get('email')
        cache_captcha = cache.get(cacheKey.EMAIL_CAPTCHA%email)
        if not cache_captcha:
            raise forms.ValidationError('验证码过期')
        if str(cache_captcha) != str(captcha):
            raise forms.ValidationError(f'验证码错误')
        return captcha


class LoginForm(forms.Form):
    email = forms.EmailField(required=True, error_messages={})
    password = forms.CharField(max_length=20, min_length=3, required=True, error_messages={})
    remember = forms.BooleanField(required=False)   # 是否保持登录状态

class PostForm(forms.Form):
    title = forms.CharField(max_length=100, min_length=1, required=True, error_messages={})
    category = forms.IntegerField(required=True)    # 存储的是category_id
    content = forms.CharField(widget=forms.Textarea, max_length=65536, min_length=4, required=True, error_messages={})
