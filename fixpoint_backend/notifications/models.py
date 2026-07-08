from django.db import models
from django.conf import settings


class Notification(models.Model):
    notificationID = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    issue = models.ForeignKey(
        'issues.Issue',
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.TextField()
    isRead = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user}: {self.message[:50]}"

    class Meta:
        db_table = 'notifications'
        ordering = ['-createdAt']