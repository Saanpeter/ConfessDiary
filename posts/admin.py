from django.contrib import admin

from .models import Bookmark, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'content_preview',
        'image_exists',
        'video_exists',
        'likes_count',
        'comments_count',
        'bookmarks_count',
        'is_archived',
        'created_at',
    )
    search_fields = ('id', 'content', 'author__username', 'author__email')
    list_filter = ('is_archived', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'edit_token')
    actions = ['archive_posts', 'restore_posts', 'bulk_delete_posts']
    fieldsets = (
        ('Content', {'fields': ('author', 'content', 'image', 'video', 'anonymous_name')}),
        ('Status', {'fields': ('is_archived', 'likes', 'created_at')}),
    )

    def content_preview(self, obj):
        return obj.content[:80] if obj.content else '—'

    content_preview.short_description = 'Content'

    def image_exists(self, obj):
        return bool(obj.image)

    image_exists.boolean = True
    image_exists.short_description = 'Image'

    def video_exists(self, obj):
        return bool(obj.video)

    video_exists.boolean = True
    video_exists.short_description = 'Video'

    def likes_count(self, obj):
        return obj.likes.count()

    likes_count.short_description = 'Likes'

    def comments_count(self, obj):
        return obj.comments.count()

    comments_count.short_description = 'Comments'

    def bookmarks_count(self, obj):
        return obj.bookmarked_by.count()

    bookmarks_count.short_description = 'Bookmarks'

    def archive_posts(self, request, queryset):
        queryset.update(is_archived=True)

    archive_posts.short_description = 'Archive selected posts'

    def restore_posts(self, request, queryset):
        queryset.update(is_archived=False)

    restore_posts.short_description = 'Restore selected posts'

    def bulk_delete_posts(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{count} posts deleted.')

    bulk_delete_posts.short_description = 'Delete selected posts'

    class Media:
        css = {'all': ('admin/css/whisperbook_admin.css',)}


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'created_at')
    search_fields = ('user__username', 'user__email', 'post__content')
    list_filter = ('created_at',)
