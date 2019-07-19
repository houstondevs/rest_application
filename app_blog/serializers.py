from rest_framework import serializers

from .models import Post,Tag


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('pk', 'author', 'title', 'text', 'publish_date', 'tags')
        read_only_fields = ('pk', 'author')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('pk', 'name')
        read_only_fields = ('pk',)
