from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from .forms import PostForm, CommentForm, EditProfileForm
from .models import Category, Comment, Post, User


class OnlyAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        return self.get_object().author == self.request.user


def get_posts(*args, **kwargs):
    return Post.objects.select_related(*args).annotate(
        comment_count=Count('comments')).filter(**kwargs).order_by('-pub_date')


def get_paginator(request, queryset,
                  number_of_pages=10):
    paginator = Paginator(queryset, number_of_pages)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    return render(request, 'blog/index.html', {
        'page_obj': get_paginator(request, get_posts(
            'author',
            'location',
            'category',
            is_published=True,
            category__is_published=True,
            pub_date__lte=datetime.now()), 10)})


def post_detail(request, post_id):
    post = get_object_or_404(get_posts(), pk=post_id)
    if post.author != request.user:
        post = get_object_or_404(
            get_posts(is_published=True,
                      category__is_published=True,
                      pub_date__lte=datetime.now()), pk=post_id)
    return render(request, 'blog/detail.html', {
        'post': post,
        'form': CommentForm(),
        'comments': post.comments.select_related('author')
    })


def category_posts(request, category_slug):
    category = get_object_or_404(Category,
                                 slug=category_slug,
                                 is_published=True)
    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': get_paginator(
            request, get_posts(
                'author',
                'location',
                'category',
                category=category,
                is_published=True,
                pub_date__lte=datetime.now()), 10)})


class ProfileDetailView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            form=CommentForm(),
            comment=self.object.comments.select_related('author').all(),
            page_obj=get_paginator(
                self.request,
                self.object.posts.select_related('author',
                                                 'location',
                                                 'category')
                .annotate(comment_count=Count('comments'))
                .order_by('-pub_date'), 10))


class EditProfileUpdateView(LoginRequiredMixin,
                            UserPassesTestMixin,
                            UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile', args={self.request.user.username})

    def test_func(self):
        return self.get_object() == self.request.user


@login_required
def create_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post.id)
    return render(request, 'blog/create.html', {'form': form})


@ login_required
def delete_post(request, post_id=None):
    instance = get_object_or_404(Post, pk=post_id)
    if instance.author != request.user:
        return redirect('blog:post_detail', post_id)
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html',
                  {'form': PostForm(instance=instance)})


def get_post_data(kwargs):
    return get_object_or_404(
        Post,
        pk=kwargs['post_id'],
        pub_date__lte=datetime.now(),
        is_published=True,
        category__is_published=True,
    )


class CommentMixin:
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])


class CommentCreateView(CommentMixin, LoginRequiredMixin, CreateView):
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentUpdateView(CommentMixin, LoginRequiredMixin, UpdateView):
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=self.kwargs[self.pk_url_kwarg])
        if self.request.user != comment.author:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class CommentDeleteView(CommentMixin, LoginRequiredMixin, DeleteView):
    def delete(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=self.kwargs[self.pk_url_kwarg])
        if self.request.user != comment.author:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().delete(request, *args, **kwargs)
