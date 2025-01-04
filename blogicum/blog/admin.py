from django.contrib import admin

from blog.models import Category, Comment, Location, Post


admin.site.empty_value_display = 'Не задано'


class PostInline(admin.TabularInline):
    model = Post
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'slug',
        'is_published',
    )
    list_editable = (
        'description',
        'slug',
        'is_published',
    )
    search_fields = ('title',)
    list_display_links = ('title',)
    inlines = (PostInline,)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published',
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('name',)
    list_display_links = ('name',)
    inlines = (PostInline,)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'created_at',
        'text',
        'pub_date',
        'is_published',
        'author',
        'location',
        'category',
    )
    list_editable = (
        'is_published',
        'pub_date',
        'author',
        'location',
        'category',
    )
    search_fields = ('title',)
    list_filter = (
        'category',
        'location',
        'created_at',
        'pub_date',
        'is_published',
    )
    list_display_links = ('title',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'post',
        'text',
        'author',
        'created_at',
    )
    list_editable = (
        'text',
        'author',
    )
    search_fields = ('text',)
    list_filter = (
        'author',
        'created_at',
    )
    list_display_links = ('post',)
