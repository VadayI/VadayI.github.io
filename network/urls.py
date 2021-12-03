
from django.urls import path

from . import views

app_name = 'network'

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add_post", views.add_post, name="add_post"),
    path("update_post", views.update_post, name="update_post"),
    path("liking", views.liking, name="liking"),
    path("get_posts", views.get_posts, name="get_posts"),
    path("profile", views.get_profile, name="profile"),
    path("following", views.following, name="following"),
    path("get_following_list", views.get_following_list, name="get_following_list"),
]
