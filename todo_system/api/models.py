from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

class Todo(models.Model):
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    due_date = models.DateTimeField()
    status = models.CharField(max_length=20)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

class TodoSharing(models.Model):
    TODO_ACCESS_CHOICES = [
        ('read_only', 'Read Only'),
        ('read_write', 'Read/Write'),
    ]
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE, related_name='sharing')
    shared_with = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    access_type = models.CharField(max_length=20, choices=TODO_ACCESS_CHOICES, default='read_only')
    approval_required = models.BooleanField(default=True)
    approved = models.BooleanField(default=False)

class TodoChangeLog(models.Model):
    STATUS_CHOICES = [
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('pending', 'Pending'),
    ]
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    change_description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    approved_by_owner = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

class AccessLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    todo_sharing = models.ForeignKey(TodoSharing, on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    activity = models.CharField(max_length=100)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.activity} - {self.timestamp}"