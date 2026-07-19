from django.contrib.auth.models import AbstractUser
from django.db import models
from cloudinary.models import CloudinaryField
from django.conf import settings as django_settings
from django.core.validators import URLValidator


class User(AbstractUser):
    is_banned = models.BooleanField(default=False)
    profile_picture = CloudinaryField('image', blank=True, null=True)
    bio = models.TextField(blank=True)
    website = models.URLField(blank=True, validators=[URLValidator()])
    location = models.CharField(max_length=100, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

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
    dark_mode = models.BooleanField(default=False)

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


class BlockedUser(models.Model):
    user = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blocked_users'
    )
    blocked_user = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blocked_by_users'
    )
    is_muted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'blocked_user')
        verbose_name = 'Blocked or muted user'
        verbose_name_plural = 'Blocked or muted users'

    def __str__(self):
        state = 'muted' if self.is_muted else 'blocked'
        return f"{self.user} has {state} {self.blocked_user}"


class Follow(models.Model):
    follower = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following'
    )
    following = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followers'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        verbose_name = 'User follow'
        verbose_name_plural = 'User follows'

    def __str__(self):
        return f"{self.follower} follows {self.following}"
 