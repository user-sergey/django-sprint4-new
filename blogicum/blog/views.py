from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from blog.forms import CommentForm, PostForm, ProfileEditForm
from blog.models import Category, Comment, Post, User
from core.constants import POSTS_BY_PAGE


def get_posts(
    posts=Post.objects,
    only_published=True,
    with_relations=True,
    with_annotations=True
):
    if with_relations:
        posts = posts.select_related('author', 'location', 'category')
    if with_annotations:
        posts = posts.annotate(
            comment_count=Count('comments')
        ).order_by(*Post._meta.ordering)
    if only_published:
        posts = posts.filter(
            is_published__exact=True,
            category__is_published__exact=True,
            pub_date__lte=timezone.now()
        )
    return posts


def paginate_posts(request, posts, posts_per_page=POSTS_BY_PAGE):
    paginator = Paginator(posts, posts_per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    page_obj = paginate_posts(request, get_posts())
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        post = get_object_or_404(get_posts(with_annotations=False), id=post_id)
    return render(
        request,
        'blog/detail.html',
        {
            'post': post,
            'comments': post.comments.select_related('author'),
            'form': CommentForm()
        }
    )


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        is_published__exact=True,
        slug=category_slug
    )
    posts = get_posts(posts=category.posts)
    return render(
        request,
        'blog/category.html',
        {'page_obj': paginate_posts(request, posts), 'category': category}
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = get_posts(
        posts=author.posts,
        only_published=request.user != author
    )
    return render(
        request,
        'blog/profile.html',
        {'page_obj': paginate_posts(request, posts), 'profile': author}
    )


@login_required
def edit_profile(request):
    form = ProfileEditForm(request.POST or None, instance=request.user)
    if not form.is_valid():
        return render(request, 'blog/user.html', {'form': form})
    form.save()
    return redirect('blog:profile', request.user.username)


@login_required
def create_post(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if not form.is_valid():
        return render(request, 'blog/create.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('blog:profile', request.user.username)


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        request.FILES or None,
        instance=post
    )
    if not form.is_valid():
        return render(request, 'blog/create.html', {'form': form})
    form.save()
    return redirect('blog:post_detail', post_id)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', request.user.username)
    return render(request, 'blog/create.html', {'form': {'instance': post}})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if not form.is_valid():
        return render(
            request,
            'blog/detail.html',
            {
                'post': post,
                'form': form,
                'comments': post.comments.select_related('author')
            }
        )
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    comment.save()
    return redirect('blog:post_detail', post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if not form.is_valid():
        return render(
            request,
            'blog/comment.html',
            {'comment': comment, 'form': form}
        )
    form.save()
    return redirect('blog:post_detail', post_id)


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id)
    return render(request, 'blog/comment.html', {'comment': comment})
