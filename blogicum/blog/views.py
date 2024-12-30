from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from .models import Post, Category, Comment
from .forms import ProfileForm, PostForm, CommentForm

User = get_user_model()


class OnlyAuthorMixin(UserPassesTestMixin):
    '''Миксин для проверки авторства'''

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


def get_posts(query_set):
    return query_set.select_related(
        'author',
        'location',
        'category'
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    )


def index(request):
    paginator = Paginator(get_posts(Post.objects), 10)
    return render(request, 'blog/index.html',
                  {'page_obj': paginator.get_page(request.GET.get('page'))})


def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.select_related(
        'author',
        'location',
        'category'), pk=post_id)
    if post.author != request.user:
        post = get_object_or_404(get_posts(Post.objects), pk=post_id)
    return render(request, 'blog/detail.html', {
        'post': post,
        'form': CommentForm(),
        'comments': post.comments.select_related('author')
    })


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True)
    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': Paginator(
            get_posts(category.posts.all()), 10).get_page(
                request.GET.get('page'))
    })


class ProfileDetailView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comment'] = (
            self.object.comments.select_related('author')).all()

        if self.request.user == self.object:
            posts = Post.objects.filter(author=self.object).select_related(
                'author', 'location', 'category')
        else:
            posts = get_posts(Post.objects).filter(author=self.get_object())

        context['page_obj'] = Paginator(posts, 10).get_page(
            self.request.GET.get('page'))
        return context


class EditProfile(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'registration/registration_form.html'

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username})


@login_required
def create_post(request, post_id=None):
    if post_id is not None:
        instance = get_object_or_404(Post, pk=post_id)
        if instance.author != request.user:
            return redirect('blog:post_detail', post_id=post_id)
    else:
        instance = None
    form = PostForm(
        request.POST or None, instance=instance, files=request.FILES or None)
    context = {'form': form}
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', context)


@login_required
def delete_post(request, post_id=None):
    instance = get_object_or_404(Post, pk=post_id)
    if instance.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    form = PostForm(instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', context)


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_instance
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment'] = None
        return context

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.post_instance.id})


class CommentUpdateView(OnlyAuthorMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        comment = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        return comment

    def get_success_url(self):
        comment = self.get_object()
        return reverse('blog:post_detail', kwargs={'post_id': comment.post.id})


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        comment = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        return comment

    def get_success_url(self):
        comment = self.get_object()
        return reverse('blog:post_detail', kwargs={'post_id': comment.post.id})
