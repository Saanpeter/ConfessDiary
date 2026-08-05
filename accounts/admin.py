from django.contrib import admin
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount

from .models import BlockedUser, Follow, Report, UserSettings

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'is_google_user',
        'is_banned',
        'is_staff',
        'last_login',
        'date_joined',
    )
    search_fields = ('id', 'username', 'email', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff', 'is_banned', 'date_joined')
    ordering = ('-date_joined',)
    readonly_fields = ('id', 'last_login', 'date_joined')
    fieldsets = (
        ('Account', {'fields': ('id', 'username', 'email', 'is_active', 'is_banned', 'is_staff')}),
        ('Profile', {'fields': ('first_name', 'last_name', 'bio', 'location', 'website', 'profile_picture')}),
        ('Dates', {'fields': ('date_joined', 'last_login')}),
    )
    actions = ['ban_users', 'unban_users']

    def is_google_user(self, obj):
        return SocialAccount.objects.filter(user=obj).exists()

    is_google_user.boolean = True
    is_google_user.short_description = 'Google user'

    def ban_users(self, request, queryset):
        queryset.update(is_banned=True)

    ban_users.short_description = 'Ban selected users'

    def unban_users(self, request, queryset):
        queryset.update(is_banned=False)

    unban_users.short_description = 'Restore selected users'

    class Media:
        css = {'all': ('admin/css/whisperbook_admin.css',)}


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_notifications', 'push_notifications', 'dark_mode', 'who_can_comment', 'media_quality')
    search_fields = ('user__username', 'user__email')
    list_filter = ('dark_mode', 'email_notifications', 'push_notifications')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'resolved', 'created_at')
    search_fields = ('id', 'user__email', 'user__username', 'message')
    list_filter = ('resolved', 'created_at')
    ordering = ('-created_at',)


@admin.register(BlockedUser)
class BlockedUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'blocked_user', 'is_muted', 'created_at')
    search_fields = ('user__username', 'blocked_user__username', 'blocked_user__email')
    list_filter = ('is_muted',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    search_fields = ('follower__username', 'following__username')
    list_filter = ('created_at',)
