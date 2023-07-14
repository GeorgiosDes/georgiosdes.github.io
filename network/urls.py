
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # API Routes
    path("posts", views.new_post, name="new_post"),
    path("posts/<str:action>", views.like_post, name="like_post"),
    path("posts/all/<int:page>", views.load_posts, name="load_posts"),
    path("comment", views.comment, name="comment"),
    path("posts/edit/<int:post_id>", views.edit_post, name="edit_post"),
    path("posts/following/<int:page>", views.load_following, name="load_following"),
    path("profile/<str:username>/<int:page>", views.load_profile, name="load_profile"),
    path("profile/<str:action>", views.follow_unfollow, name="follow_unfollow")
]
