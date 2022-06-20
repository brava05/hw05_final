from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.index, name='index'),
    # Список разделов
    path('group/', views.group_list),
    # отдельная группа
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    # Профайл пользователя
    path('profile/<str:username>/', views.profile, name='profile'),
    # Просмотр записи
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    # создание записи
    path('create/', views.post_create, name='post_create'),
    # редактирование записи
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    # добавление комментариев
    path(
        'posts/<int:post_id>/comment/', views.add_comment, name='add_comment'
    ),
    # подписка
    path('follow/', views.follow_index, name='follow_index'),
    # подписаться
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    # отписаться
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
]
