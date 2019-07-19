from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Post(models.Model):
    author = models.ForeignKey(User, verbose_name='Автор', related_name='posts', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Заглавие', blank=False, null=False, max_length=100)
    text = models.TextField(verbose_name='Текст', blank=True, null=True, max_length=1000)
    publish_date = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField('Tag', related_name='Тэги', blank=True, null=True)

    def __str__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField(verbose_name='Тэг', blank=False, null=False, unique=True, max_length=50)

    def save(self, *args, **kwargs):
        self.name = '#'+self.name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
