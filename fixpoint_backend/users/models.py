from django.db import models
from django.contrib.auth.models import AbstractUser


class Role(models.Model):
    roleID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'roles'


DEPARTMENT_CHOICES = [
    ('IT', 'Information Technology'),
    ('HR', 'Human Resources'),
    ('Engineering', 'Engineering'),
    ('Finance', 'Finance'),
    ('Operations', 'Operations'),
    ('Marketing', 'Marketing'),
    ('Management', 'Management'),
    ('Other', 'Other'),
]


class CustomUser(AbstractUser):
    # AbstractUser already has: id, username, first_name, last_name,
    # email, password, is_staff, is_active, date_joined, last_login
    department = models.CharField(
        max_length=100,
        choices=DEPARTMENT_CHOICES,
        blank=True,
        null=True
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )

    # Use email as the login field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    # Make email unique
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    class Meta:
        db_table = 'users'