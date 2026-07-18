from django.contrib.auth.models import AbstractUser
from django.db import models
from cloudinary.models import CloudinaryField
from django.conf import settings as django_settings

class User(AbstractUser):

    is_banned = models.BooleanField(default=False)

    profile_picture = CloudinaryField('image', blank=True, null=True)

    joined_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.username
    

class UserSettings(models.Model):
    COMMENT_CHOICES = [
        ('everyone', 'Everyone'),
        ('nobody', 'No one'),
    ]
    MEDIA_QUALITY_CHOICES = [
        ('high', 'High Quality'),
        ('saver', 'Data Saver'),
    ]
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('ml', 'Malayalam'),
        ('hi', 'Hindi'),
        ('es', 'Spanish'),
    ]
 
    user = models.OneToOneField(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='settings'
    )
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    who_can_comment = models.CharField(max_length=10, choices=COMMENT_CHOICES, default='everyone')
    media_quality = models.CharField(max_length=10, choices=MEDIA_QUALITY_CHOICES, default='high')
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    sound_enabled = models.BooleanField(default=True)
 
    def __str__(self):
        return f"Settings for {self.user}"
 
 
class Report(models.Model):
    user = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports'
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
 
    def __str__(self):
        return f"Report from {self.user} - {self.created_at:%Y-%m-%d}"
 