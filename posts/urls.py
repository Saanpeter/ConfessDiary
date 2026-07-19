from django.urls import path
from . import views
from django.urls import get_resolver

urlpatterns = [
    path('', views.home, name='home'),
    path('posts/', views.all_posts, name='all_posts'),
    path('posts/new/', views.new_post, name='new_post'),
    path('posts/<int:post_id>/like/', views.like_post, name='like_post'),
    path('posts/<int:post_id>/bookmark/', views.bookmark_post, name='bookmark_post'),
    path('likes/', views.my_likes, name='my_likes'),
    path('bookmarks/', views.bookmarks, name='bookmarks'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings_page, name='settings_page'),
    path('settings/profile/', views.profile_settings, name='profile_settings'),
    path('settings/activity/', views.activity_settings, name='activity_settings'),
    path('settings/archive/', views.archive_view, name='archive_view'),
    path('posts/<int:post_id>/archive/', views.toggle_archive, name='toggle_archive'),
    path('settings/notifications/', views.notification_settings, name='notification_settings'),
    path('settings/comments/', views.comment_settings, name='comment_settings'),
    path('settings/media-quality/', views.media_quality_settings, name='media_quality_settings'),
    path('settings/language-sound/', views.language_sound_settings, name='language_sound_settings'),
    path('settings/report/', views.report_problem, name='report_problem'),
    path('settings/download/', views.download_data, name='download_data'),
    path('help/', views.help_page, name='help_page'),
    path('about/', views.about_page, name='about_page'),
    path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('posts/<int:post_id>/edit/', views.edit_post, name='edit_post'),
]
