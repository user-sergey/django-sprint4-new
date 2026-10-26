from django.contrib import admin

from .models import Category, Comment, Location, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'slug', 'is_published')
    list_editable = ('is_published',)
    search_fields = ('title', 'description', 'slug')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'post', 'author', 'created_at')
    search_fields = ('text',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'pub_date',
        'category',
        'is_published',
        'created_at'
    )
    list_editable = ('pub_date', 'category', 'is_published')
    search_fields = ('title', 'text')


admin.site.register(Location)
