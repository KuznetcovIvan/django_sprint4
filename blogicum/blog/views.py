from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.generic import DetailView


from blog.models import Post, Category

User = get_user_model()


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
    return render(request, 'blog/index.html', {
        'post_list': get_posts(Post.objects)[:5]})


def post_detail(request, post_id):
    return render(request, 'blog/detail.html', {
        'post': get_object_or_404(get_posts(Post.objects), pk=post_id)})


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True)
    return render(request, 'blog/category.html', {
        'category': category,
        'post_list': get_posts(category.posts)
    })


class ProfileDetailView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['posts'] = (
            Post.objects.select_related('author').filter(author=user))
        return context
