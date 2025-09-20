from django.urls import path


from . import views
app_name = 'blog'
urlpatterns = [
    path('404', views.page_not_found, name='page_not_found'),
    path('blog/search', views.search_blog, name='search_blog'),
    path('message', views.message, name='message'),
    path('blog/<int:blog_id>/', views.blog_detail, name='blog_detail'),
    path('blog/pub', views.pub_blog, name='pub_blog'),
    path('blog/comment', views.pub_comment, name='pub_comment'),
    path('auth/login', views.csdn_login, name='login'),
    path('auth/register', views.csdn_register, name='register'),
    path('auth/logout', views.csdn_logout, name='logout'),
    path('auth/send_email_captcha', views.send_email_captcha, name='send_email_captcha'),
]
