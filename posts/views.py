# posts/views.py

from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.http import JsonResponse, HttpResponseNotAllowed
from django.utils import timezone

from .models import Post, Bookmark
from .forms import EditPostForm
from accounts.forms import ProfileEditForm
from accounts.models import Follow, UserSettings, Report, BlockedUser


def _get_or_create_settings(user):
    settings_obj, created = UserSettings.objects.get_or_create(user=user)
    return settings_obj


def _exclude_hidden_posts(request, queryset):
    if not request.user.is_authenticated:
        return queryset
    hidden_user_ids = request.user.blocked_users.values_list('blocked_user_id', flat=True)
    return queryset.exclude(author_id__in=hidden_user_ids)


def _post_hot_score(post):
    age_hours = max((timezone.now() - post.created_at).total_seconds() / 3600.0, 0.1)
    likes = getattr(post, 'likes_count', post.likes.count())
    comments = getattr(post, 'comments_count', post.comments.count())
    decay = 0.5
    return (likes * 3) + (comments * 2) - (age_hours * decay)


def _visible_comments(request, post):
    if not request.user.is_authenticated:
        return post.comments.filter(parent__isnull=True).select_related('user').prefetch_related('replies')
    hidden_user_ids = request.user.blocked_users.values_list('blocked_user_id', flat=True)
    return post.comments.filter(parent__isnull=True).exclude(user_id__in=hidden_user_ids).select_related('user').prefetch_related('replies')


def home(request):
    posts = _exclude_hidden_posts(request, Post.objects.filter(is_archived=False)).order_by('-created_at')[:20]
    return render(request, 'posts/home.html', {'posts': posts})


def all_posts(request):
    posts = _exclude_hidden_posts(request, Post.objects.filter(is_archived=False)).order_by('-created_at')
    q = request.GET.get('q')
    if q:
        posts = posts.filter(content__icontains=q)
    return render(request, 'posts/all_posts.html', {'posts': posts})


def trending(request):
    posts = _exclude_hidden_posts(request, Post.objects.filter(is_archived=False)).annotate(
        likes_count=Count('likes', distinct=True),
        comments_count=Count('comments', distinct=True),
    )
    sort = request.GET.get('sort', 'hot')
    if sort == 'new':
        posts = posts.order_by('-created_at')
    elif sort == 'top':
        posts = posts.order_by('-likes_count', '-comments_count', '-created_at')
    else:
        posts = list(posts)
        for post in posts:
            post.hot_score = _post_hot_score(post)
        posts.sort(key=lambda item: item.hot_score, reverse=True)
    return render(request, 'posts/trending.html', {
        'posts': posts,
        'active_sort': sort,
    })


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
            author=request.user if request.user.is_authenticated else None,
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
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        messages.error(request, "You can only edit your own posts.")
        return redirect('post_detail', post_id=post.id)

    if request.method == 'POST':
        form = EditPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated.")
            return redirect('post_detail', post_id=post.id)
    else:
        form = EditPostForm(instance=post)

    return render(request, 'posts/edit_post.html', {'form': form, 'post': post})
@login_required
def set_theme_preference(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    theme = request.POST.get('theme')
    if theme not in ['light', 'dark']:
        return JsonResponse({'error': 'Invalid theme'}, status=400)
    settings_obj = _get_or_create_settings(request.user)
    settings_obj.dark_mode = theme == 'dark'
    settings_obj.save()
    return JsonResponse({'theme': theme})


@login_required
def block_user(request, user_id):
    User = get_user_model()
    target = get_object_or_404(User, id=user_id)
    if target == request.user:
        messages.error(request, 'You cannot block yourself.')
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    BlockedUser.objects.update_or_create(
        user=request.user,
        blocked_user=target,
        defaults={'is_muted': False},
    )
    messages.success(request, f'You have blocked {target.username}.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def mute_user(request, user_id):
    User = get_user_model()
    target = get_object_or_404(User, id=user_id)
    if target == request.user:
        messages.error(request, 'You cannot mute yourself.')
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    BlockedUser.objects.update_or_create(
        user=request.user,
        blocked_user=target,
        defaults={'is_muted': True},
    )
    messages.success(request, f'You have muted {target.username}.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def unblock_user(request, user_id):
    User = get_user_model()
    target = get_object_or_404(User, id=user_id)
    BlockedUser.objects.filter(user=request.user, blocked_user=target).delete()
    messages.success(request, f'You have unblocked {target.username}.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def unmute_user(request, user_id):
    User = get_user_model()
    target = get_object_or_404(User, id=user_id)
    BlockedUser.objects.filter(user=request.user, blocked_user=target, is_muted=True).delete()
    messages.success(request, f'You have unmuted {target.username}.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def follow_user(request, user_id):
    User = get_user_model()
    target = get_object_or_404(User, id=user_id)
    if target == request.user:
        messages.error(request, 'You cannot follow yourself.')
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    Follow.objects.get_or_create(follower=request.user, following=target)
    messages.success(request, f'You are now following {target.username}.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def unfollow_user(request, user_id):
    User = get_user_model()
    target = get_object_or_404(User, id=user_id)
    Follow.objects.filter(follower=request.user, following=target).delete()
    messages.success(request, f'You have unfollowed {target.username}.')
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


@login_required
def profile_settings(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile settings updated.")
            return redirect('profile_settings')
    else:
        form = ProfileEditForm(instance=request.user)

    settings_obj = _get_or_create_settings(request.user)
    return render(request, 'posts/profile_settings.html', {
        'form': form,
        'settings_obj': settings_obj,
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
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        messages.error(request, "You can only delete your own posts.")
        return redirect('home')

    if request.method == 'POST':
        post.delete()
        messages.success(request, "Post deleted.")
        return redirect('home')

    return render(
        request,
        'posts/confirm_delete.html',
        {'post': post}
    )