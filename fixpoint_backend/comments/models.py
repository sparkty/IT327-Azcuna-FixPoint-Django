from django.db import models
from django.conf import settings


class Comment(models.Model):
    commentID = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    issue = models.ForeignKey(
        'issues.Issue',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.issue}"

    class Meta:
        db_table = 'comments'
        ordering = ['createdAt']