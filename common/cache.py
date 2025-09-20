from django.core.cache import cache
from django_redis import get_redis_connection

redis_client = get_redis_connection()

class CacheKey:
    EMAIL_CAPTCHA = 'email_captcha:%s'
    BLOG_FEED = 'blog_feed:%s'  # 博客流, 后面是user_id



