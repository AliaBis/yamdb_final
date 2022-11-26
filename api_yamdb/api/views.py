import random

import django_filters
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Comment, Genre, Review, Title, User

from .permissions import (AdminOnly, GetAllPostDeleteAdmin, MeOnly,
                          ReviewCommentsPermission)
from .serializers import (CategorySerializer, CommentSerializer,
                          ReviewSerializer, TitleReadSerializer,
                          GenreSerializer, SignupSerializer,
                          TitleWriteSerializer, TokenSerializer,
                          UserSerializer)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (GetAllPostDeleteAdmin,)

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class GenreViewSet(viewsets.ModelViewSet):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (GetAllPostDeleteAdmin,)

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TitleFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )

    class Meta:
        model = Title
        fields = ('name', 'year', 'genre__title', 'category__title')


class TitleViewSet(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (GetAllPostDeleteAdmin,)

    def get_queryset(self):
        queryset = Title.objects.all()
        category = self.request.query_params.get('category')
        genre = self.request.query_params.get('genre')
        if (category is not None) and (genre is not None):
            return queryset.filter(
                category=Category.objects.get(slug=category),
                genre=Genre.objects.get(slug=genre)
            )
        if category is not None:
            return queryset.filter(
                category=Category.objects.get(slug=category)
            )
        if genre is not None:
            return queryset.filter(genre=Genre.objects.get(slug=genre))
        return queryset

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (ReviewCommentsPermission,)

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs.get('pk2'))

    def get_queryset(self):
        review = self.get_review()
        return Comment.objects.filter(review=review.pk)

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user, review=self.get_review()
        )


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (ReviewCommentsPermission,)

    def get_title(self):
        return get_object_or_404(
            Title, pk=self.kwargs.get('title_id')
        )

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user, title=self.get_title()
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    search_fields = ('username',)
    lookup_field = 'username'
    permission_classes = (AdminOnly,)


class MeViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    search_fields = ('username',)
    lookup_field = 'username'
    permission_classes = (MeOnly,)

    def retrieve(self, request, *args, **kwargs):
        instance = request.user
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        instance = request.user
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )
        if request.data.get('role'):
            dict_to_operate = dict()
            for key, value in request.data.items():
                dict_to_operate[key] = value
            dict_to_operate.pop('role')
            serializer = self.get_serializer(
                instance,
                data=dict_to_operate,
                partial=True
            )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


@api_view(['POST'])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.data.get('username')
        if username == 'me':
            return Response(
                'Это имя недопустимо',
                status=status.HTTP_400_BAD_REQUEST
            )
        email = serializer.data.get('email')
        confirmation_code = str(random.randint(100000, 999999))
        send_mail(
            'Код потверджения регистрации в YamDB',
            (f'Вы зарегистрированы под именем {username}, '
                f'ваш код подтверждения: {confirmation_code}'),
            'the-third-team@praktikum.fake',
            [email, ],
            fail_silently=False,
        )
        if User.objects.filter(username=username).exists():
            found_user = User.objects.get(username=username)
            found_user.confirmation_code = confirmation_code
            found_user.save()
            return Response(
                serializer.data,
                status=status.HTTP_400_BAD_REQUEST
            )
        if User.objects.filter(email=email).exists():
            found_user = User.objects.get(email=email)
            found_user.confirmation_code = confirmation_code
            found_user.save()
            return Response(
                serializer.data,
                status=status.HTTP_400_BAD_REQUEST
            )
        User.objects.create_user(
            username=username,
            email=email,
            confirmation_code=confirmation_code)

        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def token(request):
    serializer = TokenSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.data.get('username')
        confirmation_code = serializer.data.get('confirmation_code')
        if User.objects.filter(username=username).exists():
            current_user = User.objects.get(username=username)
            if str(current_user.confirmation_code) != confirmation_code:
                return Response(
                    'Неверный код подтверждения',
                    status=status.HTTP_400_BAD_REQUEST
                )
            token = str(RefreshToken.for_user(current_user).access_token)
            current_user.confirmation_code = None
            return Response(token, status=status.HTTP_200_OK)
        else:
            return Response(
                'Пользователь не найден',
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
