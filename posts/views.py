# posts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Bookmark
from accounts.models import UserSettings, Report


def home(request):
    posts = Post.objects.all().order_by('-created_at')[:20]
    return render(request, 'posts/home.html', {'posts': posts})


def all_posts(request):
    posts = Post.objects.all().order_by('-created_at')
    q = request.GET.get('q')
    if q:
        posts = posts.filter(content__icontains=q)
    return render(request, 'posts/all_posts.html', {'posts': posts})


@login_required
def new_post(request):
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        image = request.FILES.get('image')
        video = request.FILES.get('video')

        if not content and not image and not video:
            messages.error(request, "Your confession can't be empty.")
            return redirect('new_post')

        Post.objects.create(
            author=request.user,
            content=content,
            image=image,
            video=video,
        )
        return redirect('home')

    return render(request, 'posts/new_post.html')


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def bookmark_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)
    if not created:
        bookmark.delete()
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def my_likes(request):
    posts = request.user.liked_posts.all().order_by('-created_at')
    return render(request, 'posts/placeholder.html', {
        'posts': posts,
        'page_heading': 'My Likes',
        'page_subtext': 'Confessions that moved you.',
        'page_message': "You haven't liked anything yet.",
    })


@login_required
def bookmarks(request):
    posts = Post.objects.filter(bookmarked_by__user=request.user).order_by('-created_at')
    return render(request, 'posts/placeholder.html', {
        'posts': posts,
        'page_heading': 'Bookmarks',
        'page_subtext': 'Saved for later.',
        'page_message': "No bookmarks yet.",
    })

@login_required
def profile(request):
    if request.method == 'POST':
        picture = request.FILES.get('profile_picture')
        if picture:
            request.user.profile_picture = picture
            request.user.save()
            messages.success(request, "Profile picture updated.")
        return redirect('profile')

    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    total_likes = sum(post.likes.count() for post in posts)

    return render(request, 'posts/profile.html', {
        'posts': posts,
        'total_likes': total_likes,
    })

SETTINGS_SECTIONS = {
    'report': {
        'title': 'Report a Problem',
        'message': "If you've spotted a bug or something that doesn't feel right, this is where you'll be able to send us a report soon.",
    },
    'activity': {
        'title': 'Your Activity',
        'message': "A log of your posts, likes, and comments will appear here soon.",
    },
    'notifications': {
        'title': 'Notification Settings',
        'message': "Control what you get notified about — coming soon.",
    },
    'archive': {
        'title': 'Archive',
        'message': "Archived posts (hidden from your profile but not deleted) will appear here soon.",
    },
    'comments': {
        'title': 'Comment Settings',
        'message': "Choose who can comment on your posts — coming soon.",
    },
    'media-quality': {
        'title': 'Media Quality',
        'message': "Choose how photos and videos are uploaded (data saver vs high quality) — coming soon.",
    },
    'archiving-downloading': {
        'title': 'Archiving and Downloading',
        'message': "Download a copy of your data — coming soon.",
    },
    'language-sound': {
        'title': 'Language and Sound',
        'message': "Change the app language and notification sounds — coming soon.",
    },
    'help': {
        'title': 'Help',
        'message': "Need help using Whisperbook? Support resources will be listed here soon.",
    },
    'about': {
        'title': 'About',
        'message': "Whisperbook — speak freely, stay anonymous. Version 1.0 (in development).",
    },
}


def _get_or_create_settings(user):
    settings_obj, created = UserSettings.objects.get_or_create(user=user)
    return settings_obj


@login_required
def settings_page(request):
    return render(request, 'posts/settings.html')


@login_required
def profile_settings(request):
    if request.method == 'POST':
        picture = request.FILES.get('profile_picture')
        if picture:
            request.user.profile_picture = picture
            request.user.save()
            messages.success(request, "Profile picture updated.")
        return redirect('profile_settings')

    return render(request, 'posts/profile_settings.html')


@login_required
def activity_settings(request):
    my_posts = Post.objects.filter(author=request.user).order_by('-created_at')
    liked_posts = request.user.liked_posts.all().order_by('-created_at')
    from commentsapp.models import Comment
    my_comments = Comment.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'posts/activity.html', {
        'my_posts': my_posts,
        'liked_posts': liked_posts,
        'my_comments': my_comments,
    })


@login_required
def archive_view(request):
    archived_posts = Post.objects.filter(author=request.user, is_archived=True).order_by('-created_at')
    return render(request, 'posts/archive.html', {'archived_posts': archived_posts})


@login_required
def toggle_archive(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    post.is_archived = not post.is_archived
    post.save()
    messages.success(request, "Post archived." if post.is_archived else "Post restored.")
    return redirect(request.META.get('HTTP_REFERER', 'profile'))


@login_required
def notification_settings(request):
    settings_obj = _get_or_create_settings(request.user)

    if request.method == 'POST':
        settings_obj.email_notifications = 'email_notifications' in request.POST
        settings_obj.push_notifications = 'push_notifications' in request.POST
        settings_obj.save()
        messages.success(request, "Notification settings updated.")
        return redirect('notification_settings')

    return render(request, 'posts/notification_settings.html', {'settings_obj': settings_obj})


@login_required
def comment_settings(request):
    settings_obj = _get_or_create_settings(request.user)

    if request.method == 'POST':
        settings_obj.who_can_comment = request.POST.get('who_can_comment', 'everyone')
        settings_obj.save()
        messages.success(request, "Comment settings updated.")
        return redirect('comment_settings')

    return render(request, 'posts/comment_settings.html', {'settings_obj': settings_obj})


@login_required
def media_quality_settings(request):
    settings_obj = _get_or_create_settings(request.user)

    if request.method == 'POST':
        settings_obj.media_quality = request.POST.get('media_quality', 'high')
        settings_obj.save()
        messages.success(request, "Media quality preference updated.")
        return redirect('media_quality_settings')

    return render(request, 'posts/media_quality_settings.html', {'settings_obj': settings_obj})


@login_required
def language_sound_settings(request):
    settings_obj = _get_or_create_settings(request.user)

    if request.method == 'POST':
        settings_obj.language = request.POST.get('language', 'en')
        settings_obj.sound_enabled = 'sound_enabled' in request.POST
        settings_obj.save()
        messages.success(request, "Preferences updated.")
        return redirect('language_sound_settings')

    return render(request, 'posts/language_sound_settings.html', {'settings_obj': settings_obj})


@login_required
def report_problem(request):
    if request.method == 'POST':
        message = request.POST.get('message', '').strip()
        if message:
            Report.objects.create(user=request.user, message=message)
            messages.success(request, "Thanks — your report has been sent.")
            return redirect('settings_page')
        messages.error(request, "Please describe the problem before submitting.")

    return render(request, 'posts/report_problem.html')


@login_required
def download_data(request):
    import json
    from django.http import HttpResponse
    from commentsapp.models import Comment

    posts = Post.objects.filter(author=request.user)
    comments = Comment.objects.filter(user=request.user)

    data = {
        'username': request.user.username,
        'email': request.user.email,
        'posts': [
            {'content': p.content, 'created_at': str(p.created_at)} for p in posts
        ],
        'comments': [
            {'text': c.text, 'post_id': c.post_id, 'created_at': str(c.created_at)} for c in comments
        ],
    }

    response = HttpResponse(json.dumps(data, indent=2), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="whisperbook_data.json"'
    return response


def help_page(request):
    return render(request, 'posts/help.html')


def about_page(request):
    return render(request, 'posts/about.html')

@login_required
def profile_settings(request):
    if request.method == 'POST':
        picture = request.FILES.get('profile_picture')
        if picture:
            request.user.profile_picture = picture
            request.user.save()
            messages.success(request, "Profile picture updated.")
        return redirect('profile_settings')

    return render(request, 'posts/profile_settings.html')

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        messages.error(request, "You can only delete your own posts.")
        return redirect('home')

    if request.method == 'POST':
        post.delete()
        messages.success(request, "Post deleted.")
        return redirect('home')

    return render(request, 'posts/confirm_delete.html', {'post': post})