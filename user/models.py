from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import CheckConstraint, Q, F

User = get_user_model()

# Create your models here.
class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)  # 关注者
    followed = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)  # 被关注的用户
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed')
        indexes = [
            models.Index(fields=['follower', 'followed']),  # 联合索引
            models.Index(fields=['followed']),              # 单字段索引
        ]
        constraints = [
            CheckConstraint(
                check=~Q(follower=F('followed')),
                name='prevent_self_follow'
            )
        ]