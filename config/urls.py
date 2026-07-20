from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect


def password_reset_disabled(request):
    return redirect("account_login")


urlpatterns = [
    path('admin/', admin.site.urls),

    # Disable password reset
    path(
        "accounts/password/reset/",
        password_reset_disabled,
        name="account_reset_password",
    ),

    # Allauth (Google login, logout, accounts)
    path('accounts/', include('allauth.urls')),

    # Your apps
    path('', include('posts.urls')),
    path('', include('commentsapp.urls')),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )