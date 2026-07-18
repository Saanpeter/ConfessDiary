from django.db import models
from django.conf import settings
from cloudinary_storage.storage import VideoMediaCloudinaryStorage

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    video = models.FileField(
    upload_to='videos/',
    storage=VideoMediaCloudinaryStorage(),
    blank=True,
    null=True)
    anonymous_name = models.CharField(max_length=100, default='Anonymous')
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)
    is_archived = models.BooleanField(default=False)
    
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
    
     