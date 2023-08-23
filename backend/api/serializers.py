from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from recipes import constants
from recipes.models import (Favorite, Ingredient, IngredientInRecipe,
                            Recipe, ShoppingCart, Tag)
from users.models import Subscribe, User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request.user.is_authenticated
                and request.user.follower.filter(author=obj).exists())


class RecipeToRepresentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('id', 'user', 'recipe')

    def validate(self, data):
        user = data.get('user')
        recipe = data.get('recipe')
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError({
                'errors': 'Рецепт уже добавлен в избранное'})
        return data

    def to_representation(self, instance):
        return RecipeToRepresentationSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class SubscribeGetSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipes = obj.recipe.all()
        limit = request.query_params.get('recipes_limit')
        if limit:
            try:
                limit = int(limit)
            except ValueError:
                raise serializers.ValidationError(
                    {'recipes_limit': 'Значение параметра должно быть int.'}
                )
            recipes = recipes[:int(limit)]
        return RecipeReadSerializer(
            recipes, many=True, context={'request': request}).data

    def get_recipes_count(self, obj):
        return obj.recipe.all().count()


class SubscribeCreateDeleteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscribe
        fields = ('author', 'id')

    def validate(self, data):
        user = data.get('user')
        author = data.get('author')

        if self.context.get('request').method == 'POST':
            if Subscribe.objects.filter(user=user, author=author).exists():
                raise ValidationError(
                    "Вы уже подписаны на автора")
        if user == author:
            raise ValidationError(
                detail='Подписка на самого себя невозможна',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data


class IngredientInRecipeReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        min_value=constants.LENGTH_OF_MIN_VALUE,
        max_value=constants.LENGTH_OF_MAX_AMOUNT
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=False, many=True)
    author = UserSerializer(read_only=True, many=False)
    ingredients = IngredientInRecipeReadSerializer(
        many=True,
        source='ingredient')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time'
                  )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request.user.is_authenticated
                and obj.favorite.filter(user=request.user).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request.user.is_authenticated
                and obj.shopping_carts.filter(user=request.user).exists())


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeSerializer(
        many=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        error_messages={'does_not_exist': 'Указанного тега не существует'}
    )
    image = Base64ImageField(max_length=None)
    author = UserSerializer(read_only=True)
    cooking_time = serializers.IntegerField(
        min_value=constants.LENGTH_OF_MIN_VALUE,
        max_value=constants.LENGTH_OF_MAX_TIME
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time',)

    def validate(self, data):
        tags = data.get('tags')
        ingredients = data.get('ingredients')

        if len(tags) > len(set(tags)):
            raise serializers.ValidationError({'tags': 'Теги повторяются!'})

        ingredient_ids = {ingredient['id'] for ingredient in ingredients}
        if len(ingredient_ids) > len(ingredients):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальны')

        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Выберите хотя бы один тег'})

        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Выберите хотя бы один ингредиент'})

        return data

    @staticmethod
    def create_ingredients(recipe, ingredients):
        ingredients_list = [
            IngredientInRecipe(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ]
        IngredientInRecipe.objects.bulk_create(ingredients_list)

    def create(self, validated_data):
        request = self.context.get('request', None)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        instance.tags.set(validated_data.pop('tags'))
        ingredients = validated_data.pop('ingredients')
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('id', 'user', 'recipe')

    def validate(self, data):
        user = data.get('user')
        recipe = data.get('recipe')
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError({
                'errors': 'Рецепт уже добавлен в избранное'})
        return data

    def to_representation(self, instance):
        return RecipeToRepresentationSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
