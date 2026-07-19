from django import template

register = template.Library()


@register.inclusion_tag('commentsapp/comment_item.html', takes_context=True)
def render_comment(context, comment, depth=0):
    return {
        'comment': comment,
        'depth': depth,
        'user': context['user'],
    }
