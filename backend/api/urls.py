from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api import views

app_name = 'api'

router = DefaultRouter()
router.register('recipes', views.RecipeViewSet, basename='recipes')
router.register('ingredients', views.IngredientViewSet, basename='ingredients')
router.register('tags', views.TagViewSet, basename='tags')

urlpatterns = [
    path(
        'users/subscriptions/',
        views.SubscriptionsListView.as_view(),
        name='subscriptions',
    ),
    path('users/<int:author_id>/subscribe/', views.SubscribeAPIView.as_view()),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
