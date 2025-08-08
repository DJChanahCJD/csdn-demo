from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

class Blog(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    pub_time = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-pub_time']

class Comment(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_time = models.DateTimeField(auto_now_add=True)
    blog = models.ForeignKey(Blog, related_name='comments', on_delete=models.CASCADE)

    class Meta:
        ordering = ['-pub_time']

# 重写Django默认的User成本过高，这里直接拓展
class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    avatarUrl = models.CharField(max_length=1024, blank=True)



