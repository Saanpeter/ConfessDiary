from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from posts.models import Post
from .models import Comment
from django.contrib import messages


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all().order_by('created_at')
    return render(request, 'commentsapp/post_detail.html', {
        'post': post,
        'comments': comments,
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        sticker = request.FILES.get('sticker')
        gif_url = request.POST.get('gif_url', '').strip()

        if text or sticker or gif_url:
            Comment.objects.create(
                post=post,
                user=request.user,
                text=text,
                sticker=sticker,
                gif_url=gif_url,
            )

    return redirect('post_detail', post_id=post.id)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.user != request.user:
        messages.error(request, "You can only delete your own comments.")
        return redirect('home')

    if request.method == 'POST':
        comment.delete()
        messages.success(request, "Comment deleted.")

    return redirect('post_detail', post_id=comment.post.id)