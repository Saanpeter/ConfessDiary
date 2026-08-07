from django.urls import path, include
from django.contrib import admin

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    # Admin panel
    path('admin/', admin.site.urls),

    # Authentication (Login, Signup, Google OAuth)
    path('accounts/', include('allauth.urls')),

    # Main Whisperbook posts
    path('', include('posts.urls')),

    # Comments system
    path('', include('commentsapp.urls')),

    # Notifications system
    path('', include('notifications.urls')),
]


# Serve uploaded media files during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )