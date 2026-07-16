from pathlib import Path

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

    @property
    def is_image(self):
        image_types = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        file_type = (self.fileType or '').lower()
        file_extension = Path(self.fileName or self.file.name).suffix.lower()
        return file_type in image_types or file_extension in image_extensions

    class Meta:
        db_table = 'attachments'
