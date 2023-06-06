from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("categories", views.categories, name="categories"),
    path("category/<int:id>", views.category, name="category"),
    path("create", views.create, name="create"),
    path("close_bid/<int:id>", views.close_bid, name="close_bid"),
    path("comments/<int:id>", views.comments, name="comments"),
    path("my_listings", views.my_listings, name="my_listings"),
    path("listings/<int:id>", views.listings, name="listings"),
    path("place_bid/<int:id>", views.place_bid, name="place_bid"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watchlist_action/<int:id>", views.watchlist_action, name="watchlist_action")
]
