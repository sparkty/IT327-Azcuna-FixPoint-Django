from django.db import models
from django.conf import settings


CATEGORY_CHOICES = [
    ('TECHNICAL', 'Technical'),
    ('BILLING', 'Billing'),
    ('GENERAL', 'General'),
    ('OTHER', 'Other'),
]

PRIORITY_CHOICES = [
    ('LOW', 'Low'),
    ('MEDIUM', 'Medium'),
    ('HIGH', 'High'),
    ('CRITICAL', 'Critical'),
]

STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('IN_PROGRESS', 'In Progress'),
    ('RESOLVED', 'Resolved'),
    ('CLOSED', 'Closed'),
    ('PENDING_DELETION', 'Pending Deletion'),
]


class Issue(models.Model):
    issueID = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='issues'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'issues'
        ordering = ['-createdAt']