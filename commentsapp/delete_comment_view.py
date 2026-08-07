@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post_id = comment.post.id

    if comment.user != request.user:
        return redirect('post_detail', post_id=post_id)

    if request.method == 'POST':
        comment.delete()

    return redirect('post_detail', post_id=post_id)