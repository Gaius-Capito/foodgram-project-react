from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import Subscribe, User


class UserAdmin(BaseUserAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'recipe_count',
        'follower_count',
    )

    def recipe_count(self, obj):
        return obj.recipe.count()

    recipe_count.short_description = 'Количество рецептов'

    list_filter = ('username',)

    def follower_count(self, obj):
        return obj.author.count()

    follower_count.short_description = 'Количество подписчиков'


class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'author',
    )
    list_filter = ('user',)


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
