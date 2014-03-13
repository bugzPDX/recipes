from django.contrib import admin
from recipes.models import Category, Recipe, UserProfile


class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url')

# Register your models here.

admin.site.register(Category)
admin.site.register(Recipe, PageAdmin)
admin.site.register(UserProfile)
