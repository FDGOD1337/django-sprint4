from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import CommentForm, PostForm, ProfileForm
from .models import Category, Comment, Post

POSTS_PER_PAGE = 10


def post_list():
    return Post.objects.select_related(
        'author', 'category', 'location',
    ).annotate(comment_count=Count('comments')).order_by('-pub_date', '-pk')


def published_posts(posts):
    return posts.filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True,
    )


def visible_post(request, post_id):
    post = get_object_or_404(post_list(), pk=post_id)
    if post.author_id != request.user.pk and (
        not post.is_published or post.pub_date > timezone.now()
        or post.category is None or not post.category.is_published
    ):
        raise Http404
    return post


def page(request, posts):
    return Paginator(posts, POSTS_PER_PAGE).get_page(request.GET.get('page'))


def index(request):
    return render(request, 'blog/index.html', {
        'page_obj': page(request, published_posts(post_list())),
    })


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True,
    )
    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': page(
            request, published_posts(post_list().filter(category=category)),
        ),
    })


def profile(request, username):
    owner = get_object_or_404(get_user_model(), username=username)
    posts = post_list().filter(author=owner)
    if request.user != owner:
        posts = published_posts(posts)
    return render(request, 'blog/profile.html', {
        'profile': owner,
        'page_obj': page(request, posts),
    })


@login_required
def edit_profile(request):
    form = ProfileForm(
        request.POST if request.method == 'POST' else None,
        instance=request.user,
    )
    if form.is_valid():
        user = form.save()
        return redirect('blog:profile', username=user.username)
    return render(request, 'blog/user.html', {'form': form})


def render_post(request, post, form):
    return render(request, 'blog/detail.html', {
        'post': post,
        'form': form,
        'comments': post.comments.select_related('author'),
    })


def post_detail(request, post_id):
    return render_post(request, visible_post(request, post_id), CommentForm())


def post_form(request, post=None):
    if request.method == 'POST':
        return PostForm(request.POST, request.FILES, instance=post)
    return PostForm(instance=post)


@login_required
def create_post(request):
    form = post_form(request)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user.pk != post.author_id:
        return redirect('blog:post_detail', post_id=post_id)
    form = post_form(request, post)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id, author=request.user)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {
        'form': PostForm(instance=post),
    })


@login_required
@require_POST
def add_comment(request, post_id):
    post = visible_post(request, post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render_post(request, post, form)


@login_required
def edit_comment(request, post_id, comment_id):
    visible_post(request, post_id)
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if request.user.pk != comment.author_id:
        return redirect('blog:post_detail', post_id=post_id)
    form = CommentForm(
        request.POST if request.method == 'POST' else None, instance=comment,
    )
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', {
        'form': form, 'comment': comment,
    })


@login_required
def delete_comment(request, post_id, comment_id):
    visible_post(request, post_id)
    comment = get_object_or_404(
        Comment, pk=comment_id, post_id=post_id, author=request.user,
    )
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', {'comment': comment})
