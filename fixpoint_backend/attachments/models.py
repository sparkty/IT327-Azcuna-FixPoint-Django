from django.db import models


class Attachment(models.Model):
    attachmentID = models.AutoField(primary_key=True)
    issue = models.ForeignKey(
        'issues.Issue',
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    # FK_userID is crossed out in your ERD — omitted intentionally
    file = models.FileField(upload_to='attachments/')  # goes to Supabase Storage
    fileName = models.CharField(max_length=255)
    fileType = models.CharField(max_length=50)
    fileSize = models.PositiveIntegerField(help_text='File size in bytes')

    def __str__(self):
        return self.fileName

    class Meta:
        db_table = 'attachments'