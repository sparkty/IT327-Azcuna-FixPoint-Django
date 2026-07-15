# fixpoint_backend/delete_requests/models.py
from django.db import models
from django.conf import settings


class DeleteRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    deleteRequestID = models.AutoField(primary_key=True)
    issue = models.ForeignKey(
        'issues.Issue',
        on_delete=models.CASCADE,
        related_name='delete_requests'
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='delete_requests'
    )
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'delete_requests'

    def __str__(self):
        return f"DeleteRequest(issue={self.issue_id}, status={self.status})"