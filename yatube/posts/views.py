from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm
from .utils import get_paginators_page


def index(request):
    """ Главная страница сайта. Показывает последние опубликованные статьи"""
    posts = Post.objects.select_related('author', 'group').all()
    page_obj = get_paginators_page(posts, request)

    return render(
        request,
        'posts/index.html',
        {
            'page_obj': page_obj,
            'index': True,
            'follow': False
        }
    )


def group_posts(request, slug):
    """ Выводится информация о группе и последние статьи группы."""

    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author').all()
    page_obj = get_paginators_page(posts, request)

    return render(
        request,
        'posts/group_list.html',
        {'group': group, 'page_obj': page_obj})


def group_list(request):
    """ Возвращает список всех существующих групп."""

    groups = Group.objects.all()

    return render(
        request,
        'posts/group.html',
        {'groups': groups})


def profile(request, username):
    """ Показывает информацию об авторе и его статьи."""

    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('group').all()
    page_obj = get_paginators_page(posts, request)

    following = (request.user.is_authenticated
                 and Follow.objects.filter(
                     user=request.user, author=author).exists())

    return render(
        request,
        'posts/profile.html',
        {'author': author,
         'page_obj': page_obj,
         'following': following})


def post_detail(request, post_id):
    """ Показывает информацию о конкретной статье."""

    post = get_object_or_404(Post, pk=post_id)

    form = CommentForm()
    return render(request,
                  'posts/post_detail.html',
                  {'post': post, 'form': form})


@login_required
def post_create(request):
    """ Создает новый пост."""

    if request.method != 'POST':
        form = PostForm()
        return render(request, 'posts/create_post.html', {'form': form})

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )

    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})

    post = form.save(commit=False)
    post.author = request.user
    post.save()

    return redirect('posts:profile', request.user.username)


@login_required
def post_edit(request, post_id):
    """ Редактирует пост."""

    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post
        )
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect('posts:post_detail', post_id)

        # если не валидна, то открываем опять для редактирования
        return render(
            request,
            'posts/create_post.html',
            {'form': form, 'is_edit': True, 'post_id': post_id})

    if request.user != post.author:
        # если не автор, то открываем только для просмотра
        return redirect('posts:post_detail', post_id)

    form = PostForm(instance=post)
    return render(
        request,
        'posts/create_post.html',
        {'form': form, 'is_edit': True, 'post_id': post_id})


@login_required
def add_comment(request, post_id):
    # Получите пост

    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Страница подписки. Показывает последние опубликованные статьи авторов,
    на которых подписан пользователь."""
    posts = Post.objects.filter(author__following__user=request.user)

    page_obj = get_paginators_page(posts, request)

    return render(
        request,
        'posts/index.html',
        {
            'page_obj': page_obj,
            'follow': True
        }
    )


@login_required
def profile_follow(request, username):

    author = get_object_or_404(User, username=username)

    if Follow.objects.filter(
        user=request.user,
        author=author
    ).exists() or author == request.user:
        return redirect('posts:follow_index')

    # если дошли сюда, значит можно создавать подписку
    Follow.objects.create(
        user=request.user,
        author=author
    )

    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    # Отписка
    author = get_object_or_404(User, username=username)
    follows = Follow.objects.filter(user=request.user, author=author)
    if follows.exists():
        follows.delete()

    return redirect('posts:follow_index')
