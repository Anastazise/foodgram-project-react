from datetime import datetime
import logging
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favourite, Ingredient, Components, Recipe,
                            Basket, Tag)

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeShortSerializer,
                          TagSerializer, RecipeSerializer, CreateRecipeSerializer)

logger = logging.getLogger("django")


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewSet(ModelViewSet):
    logger.info('------>CREATE<-------')
    print("ТЕКСТ ЛОГА")
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def post(self, request):
        logger.debug('------>CREATE<-------')
        print("ТЕКСТ ЛОГА")
        ser = CreateRecipeSerializer(data=request.data)
        print("Platform is running at risk")
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response({'post': ser.data})

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_to(Favourite, request.user, pk)
        else:
            return self.delete_from(Favourite, request.user, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def basket(self, request, pk):
        if request.method == 'POST':
            return self.add_to(Basket, request.user, pk)
        else:
            return self.delete_from(Basket, request.user, pk)

    def add_to(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors': 'Рецепт уже добавлен'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_basket(self, request):
        user = request.user
        if not user.basket.exists():
            return Response(status=HTTP_400_BAD_REQUEST)

        ingredients = Components.objects.filter(
            recipe__basket__user=request.user
        ).values(
            'ingredient_name',
            'ingredient_unit'
        ).annotate(amount=Sum('amount'))

        today = datetime.today()
        basket_list = (
            f'Список покупок для: {user.get_full_name()}\n\n'
            f'Дата: {today:%Y-%m-%d}\n\n'
        )
        basket_list += '\n'.join([
            f'- {ingredient["ingredient_name"]} '
            f'({ingredient["ingredient_unit"]})'
            f' - {ingredient["amount"]}'
            for ingredient in ingredients
        ])
        basket_list += f'\n\nFoodgram ({today:%Y})'

        filename = f'{user.username}_basket_list.txt'
        response = HttpResponse(basket_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
