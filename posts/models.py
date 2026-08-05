import uuid

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from cloudinary_storage.storage import VideoMediaCloudinaryStorage


def get_video_storage():
    cloud_name = (settings.CLOUDINARY_STORAGE.get('CLOUD_NAME') or '').strip()
    api_key = (settings.CLOUDINARY_STORAGE.get('API_KEY') or '').strip()
    api_secret = (settings.CLOUDINARY_STORAGE.get('API_SECRET') or '').strip()

    if cloud_name and api_key and api_secret and not any(value in {'your_cloud_name', 'your_api_key', 'your_api_secret'} for value in (cloud_name, api_key, api_secret)):
        return VideoMediaCloudinaryStorage()

    return FileSystemStorage(location=str(settings.MEDIA_ROOT / 'videos'), base_url=f'{settings.MEDIA_URL}videos/')


class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    content = models.TextField(blank=True, default='')

    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True
    )

    video = models.FileField(
        upload_to='videos/',
        storage=get_video_storage(),
        blank=True,
        null=True
    )

    @property
    def image_url(self):
        return self.image.url if self.image and hasattr(self.image, 'url') else ''

    @property
    def video_url(self):
        return self.video.url if self.video and hasattr(self.video, 'url') else ''

    anonymous_name = models.CharField(
        max_length=100,
        default='Anonymous'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_posts',
        blank=True
    )

    is_archived = models.BooleanField(default=False)

    edit_token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.anonymous_name} - {self.created_at}"
    

class Bookmark(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookmarks'
    )
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='bookmarked_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user} bookmarked post {self.post_id}"
    
     