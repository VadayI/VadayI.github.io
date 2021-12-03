from typing import ChainMap
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields import BooleanField, CharField, DateTimeField, TextField
from django.db.models.fields.related import ForeignKey
from django.views.generic import ListView


class User(AbstractUser):
    pass

class Post(models.Model):
    title = CharField(max_length=100)
    author = ForeignKey(User, blank=False, related_name='posts', on_delete=CASCADE)
    content = TextField(max_length=2000, default='', blank=False)
    status = BooleanField(default=False)
    creating_date = DateTimeField(auto_now_add=True)
    modificate_date = DateTimeField(auto_now_add=True)

class PostList(ListView):
    paginate_by = 10
    model = Post

class Follower(models.Model):
    user = ForeignKey(User, blank=False, related_name='following', on_delete=CASCADE)
    follower = ForeignKey(User, blank=False, related_name='followers', on_delete=CASCADE)
    create_date = DateTimeField(auto_now_add=True)

class Like(models.Model):
    user = ForeignKey(User, blank=False, related_name='likes', on_delete=CASCADE)
    post = ForeignKey(Post, blank=False, related_name='likes', on_delete=CASCADE)
    create_date = DateTimeField(auto_now_add=True)