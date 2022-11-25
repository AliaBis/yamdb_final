from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet, MeViewSet,
                    ReviewViewSet, TitleViewSet, UserViewSet, signup, token)

router_v1 = DefaultRouter()

router_v1.register(r'titles', TitleViewSet, basename='titles')
router_v1.register(r'categories', CategoryViewSet)
router_v1.register(r'genres', GenreViewSet)
router_v1.register(
    r'titles/(?P<pk1>[^/.]+)/reviews/(?P<pk2>[^/.]+)/comments',
    CommentViewSet,
    basename='comments'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='reviews'
)
router_v1.register(r'users', UserViewSet)


urlpatterns = [
    path(
        'v1/users/me/',
        MeViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'}),
        name='signup'
    ),
    path('v1/auth/signup/', signup, name='signup'),
    path('v1/auth/token/', token, name='token'),
    path('v1/', include(router_v1.urls)),
]
