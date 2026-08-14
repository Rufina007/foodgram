from djoser.serializers import (
    UserCreateSerializer as BaseUserCreateSerializer,
    UserSerializer as BaseUserSerializer,
)
from rest_framework import serializers

from recipes.constants import MIN_INGREDIENT_AMOUNT
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import User

from .fields import Base64ImageField


class UserCreateSerializer(BaseUserCreateSerializer):

    class Meta(BaseUserCreateSerializer.Meta):
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'password',
        )


class UserSerializer(BaseUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed', 'avatar',
        )

    def get_is_subscribed(self, author):
        request = self.context.get('request')
        return bool(
            request
            and request.user.is_authenticated
            and author.subscribers.filter(user=request.user).exists()
        )


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=MIN_INGREDIENT_AMOUNT)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeMinifiedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        many=True, read_only=True, source='recipe_ingredients',
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    def _is_in(self, related_manager):
        request = self.context.get('request')
        return bool(
            request
            and request.user.is_authenticated
            and related_manager.filter(user=request.user).exists()
        )

    def get_is_favorited(self, recipe):
        return self._is_in(recipe.favorites)

    def get_is_in_shopping_cart(self, recipe):
        return self._is_in(recipe.shoppingcarts)


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientWriteSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(),
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'ingredients', 'tags', 'image', 'name', 'text',
            'cooking_time',
        )

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError(
                'Нужно загрузить изображение.',
            )
        return value

    def validate(self, data):
        for field, message in (
            ('ingredients', 'Нужно указать хотя бы один ингредиент.'),
            ('tags', 'Нужно указать хотя бы один тег.'),
        ):
            if field not in data:
                raise serializers.ValidationError(
                    {field: 'Это поле обязательно.'},
                )
            if not data[field]:
                raise serializers.ValidationError({field: message})

        ingredient_ids = [item['id'] for item in data['ingredients']]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {'ingredients': 'Ингредиенты не должны повторяться.'},
            )
        if len(data['tags']) != len(set(data['tags'])):
            raise serializers.ValidationError(
                {'tags': 'Теги не должны повторяться.'},
            )
        return data

    @staticmethod
    def _set_ingredients(recipe, ingredients_data):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=item['id'],
                amount=item['amount'],
            )
            for item in ingredients_data
        )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self._set_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        instance.recipe_ingredients.all().delete()
        self._set_ingredients(instance, ingredients_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class UserWithRecipesSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes', 'recipes_count',
        )

    def get_recipes(self, author):
        request = self.context.get('request')
        recipes = author.recipes.all()
        limit = request.query_params.get('recipes_limit') if request else None
        if limit and limit.isdigit():
            recipes = recipes[:int(limit)]
        return RecipeMinifiedSerializer(
            recipes, many=True, context=self.context,
        ).data

    def get_recipes_count(self, author):
        return author.recipes.count()
