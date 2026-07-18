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