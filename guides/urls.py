from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("login", views.login_view, name="login"),
    path("profile", views.profile, name="profile"),
    path("profile/change_email", views.change_email, name="change_email"),
    path("profile/change_password", views.change_password, name="change_password"),
    path("guides", views.guides, name="guides"),
    path("guides/<int:game_id>/<str:sort>", views.sort_guides, name="sort_guides"),
    path("guide/<int:guide_id>", views.full_guide, name="full_guide"),
    path("news", views.news, name="news"),
    path("news/<int:game_id>/<str:sort>", views.sort_news, name="sort_news"),
    path("new/<int:new_id>", views.full_new, name="full_new"),
    path("create/<str:type>", views.create, name="create"),
    path("search", views.search, name="search"),
    path("comment", views.comment, name="comment"),

    # API Routes
    path("show_more/<str:type>/<int:game_id>/<int:page>/<int:amount>/<str:sort>", views.show_more, name="show_more"),
]