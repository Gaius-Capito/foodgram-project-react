from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientInRecipeInline, )
    list_display = (
        'id',
        'name',
        'author',
        'ingredient_list',
        'favorite_count',
    )
    list_filter = ('name', 'author', 'tags',)

    def ingredient_list(self, obj):
        return ', '.join([str(ingredient) for ingredient
                          in obj.ingredients.all()])

    ingredient_list.short_description = 'Ингредиенты'

    def favorite_count(self, obj):
        return obj.favorite.count()

    favorite_count.short_description = 'Количество добавлений в Избранное'


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug',
        'color',
    )
    list_filter = ('name',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'user',
    )
    list_filter = ('user',)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    list_filter = ('user',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
