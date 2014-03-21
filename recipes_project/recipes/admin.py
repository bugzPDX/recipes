from django.contrib import admin
from recipes.models import Category, Recipe, UserProfile, Ingredient, Unit, RecipeIngredient


class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url')

# Register your models here.

admin.site.register(Category)
admin.site.register(Ingredient)
admin.site.register(Unit)
admin.site.register(RecipeIngredient)
admin.site.register(Recipe, PageAdmin)
admin.site.register(UserProfile)
