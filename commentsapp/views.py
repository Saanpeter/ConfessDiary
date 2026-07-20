from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from posts.models import Post
from .models import Comment
from .forms import CommentForm


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    all_comments = post.comments.select_related('user').prefetch_related('replies').order_by('created_at')
    comments = [comment for comment in all_comments if comment.parent_id is None]
    form = CommentForm()
    return render(request, 'commentsapp/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        if post.author.blocked_users.filter(blocked_user=request.user).exists():
            messages.error(request, 'You cannot comment on this post.')
            return redirect('post_detail', post_id=post.id)

        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            
            # Handle parent comment (reply)
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    parent_comment = Comment.objects.get(id=parent_id, post=post)
                    comment.parent = parent_comment
                except Comment.DoesNotExist:
                    messages.error(request, 'Invalid parent comment.')
                    return redirect('post_detail', post_id=post.id)
            
            comment.save()
        else:
            messages.error(request, 'Could not submit your comment. Please make sure you entered text, sticker, or GIF.')
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