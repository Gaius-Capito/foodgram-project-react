from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscribe, User
from .filters import IngredientFilter, RecipeFilter
from .pagination import PageLimitPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateSerializer, ShoppingCartSerializer,
                          SubscribeGetSerializer,
                          SubscribeCreateDeleteSerializer, TagSerializer,
                          RecipeReadSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().select_related(
        'author'
    ).prefetch_related('tags', 'ingredients')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    serializer_class = RecipeCreateSerializer
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = PageLimitPagination

    @staticmethod
    def favorite_shopping_cart(serializers, request, pk):
        context = {'request': request}
        data = {
            'user': request.user.id,
            'recipe': pk
        }
        serializer = serializers(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def send_message(ingredients):
        text_parts = ['Список покупок:\n']

        for item in ingredients:
            ingredient_name = item["ingredient__name"]
            amount = item["amount"]
            measurement_unit = item["ingredient__measurement_unit"]
            text_parts.append(
                f'{ingredient_name} - {amount} {measurement_unit}\n')

        text = ''.join(text_parts)

        response = HttpResponse(text, content_type='text/plain')
        response[
            'Content-Disposition'] = 'attachment; filename=shopping_list.txt'
        return response

    @action(
        detail=True,
        methods=['post'],
        url_path='favorite',
        url_name='favorite',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, pk):
        return self.favorite_shopping_cart(FavoriteSerializer, request, pk)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        get_object_or_404(
            Favorite,
            user=request.user,
            recipe=get_object_or_404(Recipe, pk=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        url_path='shopping_cart',
        url_name='shopping_cart',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self.favorite_shopping_cart(
            ShoppingCartSerializer,
            request,
            pk
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        get_object_or_404(
            ShoppingCart,
            user=request.user.id,
            recipe=get_object_or_404(Recipe, pk=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):

        if not ShoppingCart.objects.filter(user=request.user).exists():
            return Response(
                {'Ошибка': 'Ваш список покупок пуст'},
                status=status.HTTP_400_BAD_REQUEST
            )
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_carts__user=request.user).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount')).order_by('ingredient__name')
        return self.send_message(ingredients)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeCreateSerializer


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)


class SubscriptionsListView(ListAPIView):
    serializer_class = SubscribeGetSerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = PageLimitPagination
    queryset = Subscribe.objects.all()

    def get_queryset(self):
        return User.objects.filter(author__user=self.request.user)


class SubscribeAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request, author_id):
        author = get_object_or_404(User, id=author_id)
        data = {'author': author.id}
        serializer = SubscribeCreateDeleteSerializer(
            data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, author_id):
        user = request.user
        author = get_object_or_404(User, id=author_id)
        subscription = Subscribe.objects.filter(author=author, user=user)
        if not subscription.exists():
            return Response(
                {'errors': 'Вы не подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
