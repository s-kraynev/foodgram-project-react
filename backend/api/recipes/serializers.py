from collections import OrderedDict

from rest_framework import serializers
from rest_framework.fields import SkipField
from rest_framework.relations import PKOnlyObject

from api.common.serializer_fields import Base64ImageField
from api.tags.serializers import TagSerializer
from api.users.serializers import UserSerializer
from ingredients.models import Ingredient
from recipes.models import Favorite, Recipe, UsedIngredient
from tags.models import Tag


class UsedIngredientReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsedIngredient
        fields = ('id', 'amount', 'name', 'measurement_unit')

    def to_representation(self, instance):
        return {
            'id': instance.ingredient.id,
            'name': instance.ingredient.name,
            'measurement_unit': instance.ingredient.measurement_unit,
            'amount': instance.amount
        }


class RecipeReadSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True, allow_null=False)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(required=True, many=True)
    ingredients = UsedIngredientReadSerializer(
        source='recipe', required=True, many=True)
    author = UserSerializer(required=True, many=False)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
        )
        read_only_fields = ('pub_date',)

    def get_is_favorited(self, obj):
        return Recipe.is_favorited(obj, self.context['request'].user.id)

    def get_is_in_shopping_cart(self, obj):
        return Recipe.is_in_shopping_cart(obj, self.context['request'].user.id)


class UsedIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        required=True, queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(required=True)

    class Meta:
        model = UsedIngredient
        fields = ('id', 'amount')

    def to_representation(self, instance):
        ret = OrderedDict()
        fields = self._readable_fields

        for field in fields:
            try:
                # custom handling for amount
                if field.field_name == 'amount':
                    attribute = (
                        instance.used_ingredient.filter(
                            recipe=self.root.instance
                        )
                        .get()
                        .amount
                    )
                else:
                    attribute = field.get_attribute(instance)
            except SkipField:
                continue

            # We skip `to_representation` for `None` values so that fields do
            # not have to explicitly deal with that case.
            #
            # For related fields with `use_pk_only_optimization` we need to
            # resolve the pk value.
            check_for_none = (
                attribute.pk
                if isinstance(attribute, PKOnlyObject)
                else attribute
            )
            if check_for_none is None:
                ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret


class RecipeWriteSerializer(serializers.ModelSerializer):
    # NOTE: it was already allow_null=False on previous review too :)
    image = Base64ImageField(required=True, allow_null=False)
    tags = serializers.ListSerializer(
        required=True,
        child=serializers.PrimaryKeyRelatedField(
            required=True, queryset=Tag.objects.all()
        ),
    )
    ingredients = UsedIngredientCreateSerializer(many=True, required=True)

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = (
            'author',
            'pub_date',
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            recipe.tags.add(tag)
        for ingredient in ingredients:
            UsedIngredient.objects.create(
                **{
                    'recipe': recipe,
                    'amount': ingredient['amount'],
                    'ingredient': ingredient['id'],
                }
            )
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        tags = validated_data.pop('tags')
        instance.tags.set(tags)

        ingredients = validated_data.pop('ingredients')
        for ingr in instance.ingredients.all():
            used_ingr = UsedIngredient.objects.get(
                recipe=instance, ingredient=ingr
            )
            used_ingr.delete()
        for ingredient in ingredients:
            UsedIngredient.objects.create(
                **{
                    'recipe': instance,
                    'amount': ingredient['amount'],
                    'ingredient': ingredient['id'],
                }
            )

        instance.save()
        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'
        read_only_fields = ('id', 'recipe', 'user')
