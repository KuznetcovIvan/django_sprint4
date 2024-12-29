from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView

from blog.models import Post, Category
from blog.forms import ProfileForms

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
    paginator = Paginator(get_posts(Post.objects), 10)
    return render(request, 'blog/index.html',
                  {'page_obj': paginator.get_page(request.GET.get('page'))})


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
        context['page_obj'] = Paginator(get_posts(Post.objects).filter(
            author=self.get_object()), 10).get_page(
                self.request.GET.get('page'))
        return context


class EditProfile(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForms
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('blog:profile')
