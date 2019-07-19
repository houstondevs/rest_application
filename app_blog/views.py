from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import permissions

from .models import Post, Tag
from .serializers import (PostSerializer, TagSerializer)
from api.permissions import IsObjectOwnerWithCreate


class PostView(mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 mixins.RetrieveModelMixin,
                 mixins.UpdateModelMixin,
                 viewsets.GenericViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsObjectOwnerWithCreate, permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(author = self.request.user)


class TagView(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)

