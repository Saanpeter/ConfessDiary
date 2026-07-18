# posts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Bookmark


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
    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'posts/placeholder.html', {
        'posts': posts,
        'page_heading': 'Profile',
        'page_subtext': f"@{request.user.username}",
        'page_message': "You haven't posted anything yet.",
    })


@login_required
def settings_page(request):
    return render(request, 'posts/placeholder.html', {
        'page_heading': 'Settings',
        'page_subtext': 'Manage your account.',
        'page_message': 'Settings options are coming soon.',
    })

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