from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):

    is_banned = models.BooleanField(default=False)

    profile_picture = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
    )

    joined_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.username