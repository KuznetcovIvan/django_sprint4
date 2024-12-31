from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('',
         views.index,
         name='index'),

    path('posts/create/',
         views.create_post,
         name='create_post'),
    path('posts/<int:post_id>/edit/',
         views.create_post,
         name='edit_post'),
    path('posts/<int:post_id>/delete/',
         views.delete_post,
         name='delete_post'),
    path('posts/<int:post_id>/',
         views.post_detail,
         name='post_detail'),

    path('posts/<int:post_id>/comment/',
         views.CommentCreateView.as_view(),
         name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         views.CommentUpdateView.as_view(),
         name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         views.CommentDeleteView.as_view(),
         name='delete_comment'),

    path('category/<slug:category_slug>/',
         views.category_posts,
         name='category_posts'),

    path('profile/edit/',
         views.EditProfileUpdateView.as_view(),
         name='edit_profile'),
    path('profile/<str:username>/',
         views.ProfileDetailView.as_view(),
         name='profile'),
]
