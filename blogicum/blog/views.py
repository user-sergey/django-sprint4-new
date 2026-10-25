from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from blog.forms import CommentForm, PostForm, ProfileEditForm
from blog.models import Category, Comment, Post
from core.constants import POSTS_BY_PAGE

User = get_user_model()


def get_queryset(only_published=True):
    queryset = Post.objects.select_related(
        'author', 'location', 'category'
    ).annotate(comment_count=Count('comments'))
    if only_published:
        queryset = queryset.filter(
            is_published__exact=True,
            category__is_published__exact=True,
            pub_date__lte=timezone.now()
        )
    return queryset.order_by('-pub_date')


def paginate_posts(requset, queryset):
    paginator = Paginator(queryset, POSTS_BY_PAGE)
    page_number = requset.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    posts = get_queryset(only_published=True)
    page_obj = paginate_posts(request, posts)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, post_id):
    queryset = Post.objects.select_related('author', 'location', 'category')
    post = get_object_or_404(queryset, id=post_id)
    is_visible = (
        post.is_published
        and post.category.is_published
        and post.pub_date <= timezone.now()
    )
    if not is_visible and request.user != post.author:
        raise Http404
    return render(
        request,
        'blog/detail.html',
        {'post': post, 'comments': post.comments.all(), 'form': CommentForm()}
    )


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        is_published__exact=True,
        slug=category_slug
    )
    posts = get_queryset(only_published=True).filter(category=category)
    page_obj = paginate_posts(request, posts)
    return render(
        request,
        'blog/category.html',
        {'page_obj': page_obj, 'category': category}
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    if request.user == author:
        posts = get_queryset(only_published=False).filter(author__exact=author)
    else:
        posts = get_queryset(only_published=True).filter(author__exact=author)
    page_obj = paginate_posts(request, posts)
    return render(
        request,
        'blog/profile.html',
        {'page_obj': page_obj, 'profile': author}
    )


@login_required
def edit_profile(request):
    form = ProfileEditForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/user.html', {'form': form})


@login_required
def create_post(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post.id)
    form = PostForm(
        request.POST or None,
        request.FILES or None,
        instance=post
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post.id)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post.id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': {'instance': post}})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('blog:post_detail', post_id=post.id)
    return render(
        request,
        'blog/detail.html',
        {'post': post, 'form': form, 'comments': post.comments.all()}
    )


@login_required
def edit_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, pk=post_id)
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author or comment.post != post:
        raise Http404
    form = CommentForm(request.POST or None, instance=comment)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post.id)
    return render(
        request,
        'blog/comment.html',
        {'comment': comment, 'form': form}
    )


@login_required
def delete_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, pk=post_id)
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author or comment.post != post:
        raise Http404
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post.id)
    return render(request, 'blog/comment.html', {'comment': comment})
