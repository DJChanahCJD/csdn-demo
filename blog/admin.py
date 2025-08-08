from django.contrib import admin
from .models import Category, Blog, Comment

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'content', 'pub_time', 'category', 'author']

class CommentAdmin(admin.ModelAdmin):
    list_display = ['content', 'pub_time', 'author', 'blog']

admin.site.register(Category, CategoryAdmin)
admin.site.register(Blog, PostAdmin)
admin.site.register(Comment, CommentAdmin)
