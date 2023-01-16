from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets, status, filters, serializers
from rest_framework.response import Response
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.tokens import default_token_generator
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework import mixins
from .permissions import (
    AdminReadOnly,
    AdminModeratorAuthorReadOnly,
    AdminPermission,
)
from reviews.models import (Review,
                            Category, Genre,
                            Title, User)
from .filters import TitleFilter
from .serializers import (ReviewSerializer, CommentSerializer,
                          CategorySerializer, GenreSerializer,
                          TitlesGetSerializer, TitlesPostSerializer,
                          RegistrationSerializer, TokenSerializer,
                          UserSerializer, ProfileEditSerializer,)
from rest_framework.pagination import PageNumberPagination


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminPermission,)
    pagination_class = PageNumberPagination
    lookup_field = 'username'

    @action(
        detail=False,
        methods=["GET", "PATCH"],
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        if request.method == "PATCH":
            serializer = ProfileEditSerializer(
                request.user, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST", ])
@permission_classes([permissions.AllowAny])
def registration(request):
    if request.method == "POST":
        data = {}
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            data['username'] = user.username
            data['email'] = user.email
            code = default_token_generator.make_token(user)
            send_mail(
                subject="yamdb registrations",
                message=f"Пользователь {user.username} успешно"
                f"зарегистрирован.\n"
                f"Код подтверждения: {code}",
                from_email=None,
                recipient_list=[user.email],
            )
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(data, status=status.HTTP_200_OK)


@api_view(["POST", ])
@permission_classes([permissions.AllowAny])
def email_verification(request):
    serializer = TokenSerializer(data=request.data)
    data = {}
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    user = get_object_or_404(
        User, username=serializer.validated_data["username"]
    )
    code = serializer.validated_data["confirmation_code"]
    print('codee', code)
    if default_token_generator.check_token(user, code):
        token = AccessToken.for_user(user)
        data["token"] = str(token)
        return Response(data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryGenreViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                           mixins.DestroyModelMixin, viewsets.GenericViewSet):
    permission_classes = [AdminReadOnly,]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(CategoryGenreViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = TitlesPostSerializer
    permission_classes = [AdminReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitlesGetSerializer
        return TitlesPostSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [AdminModeratorAuthorReadOnly,
                          IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            pk=self.kwargs.get('title_id')
        )
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [AdminModeratorAuthorReadOnly,
                          IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            pk=self.kwargs.get('title_id')
        )
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title=title
        )
        return review.comments.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            pk=self.kwargs.get('title_id')
        )
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title=title
        )
        serializer.save(
            author=self.request.user, review=review)
