from django.urls import path
from . import views

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
    path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
]
