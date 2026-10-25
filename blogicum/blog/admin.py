from django.contrib import admin

from .models import Category, Location, Post


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'slug', 'is_published')
    list_editable = ('is_published',)
    search_fields = ('title', 'description', 'slug')


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


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location)
admin.site.register(Post, PostAdmin)
