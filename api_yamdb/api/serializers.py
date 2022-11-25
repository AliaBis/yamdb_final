from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from reviews.models import (CHOICES, Category, Comment, Genre, Review, Title,
                            User)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug',)
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug',)
        lookup_field = 'slug'


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)
    description = serializers.CharField(required=False)

    class Meta:
        model = Title
        fields = ('__all__')


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all())
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all())

    rating = serializers.IntegerField(read_only=True)

    description = serializers.CharField(required=False)

    year = serializers.IntegerField(required=True)

    class Meta:
        model = Title
        fields = ('__all__')


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault())

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date', )


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault())
    title = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name')

    class Meta:
        model = Review
        fields = ('__all__')

    def validate(self, data):
        if self.context.get('request').method != 'POST':
            return data
        reviewer = self.context.get('request').user
        title_id = self.context.get('view').kwargs['title_id']
        if Review.objects.filter(author=reviewer, title_id=title_id).exists():
            raise serializers.ValidationError(
                'Вы уже написали обзор на это произведение'
            )
        return data

    def validate_score(self, value):
        if 0 < value < 11:
            return value
        raise serializers.ValidationError(
            'Я принимаю оценки от 1 до 10!'
        )


class UserSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(required=False)
    role = serializers.ChoiceField(required=False, choices=CHOICES)
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='Имя пользователя занято'
        )]
    )
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='Email занят'
        )]
    )

    class Meta:
        model = User
        # в модели 16 полей,
        # эксклюдить 10 кажется более громоздко,
        # чем объявить 6
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )


class SignupSerializer(serializers.Serializer):
    regex = RegexValidator(
        r'^[\w.@+-]+\Z$',
        'Letters, digits and @/./+/-/_ only.'
    )
    username = serializers.CharField(max_length=150, validators=[regex])
    email = serializers.EmailField(max_length=254)


class TokenSerializer(serializers.Serializer):
    regex = RegexValidator(
        r'^[\w.@+-]+\Z$',
        'Letters, digits and @/./+/-/_ only.'
    )
    username = serializers.CharField(max_length=150, validators=[regex])
    confirmation_code = serializers.CharField(max_length=10)
