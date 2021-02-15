from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("<int:auction_id>", views.auction, name="auction"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("addWatchlist/<int:auction_id>", views.addWatchlist, name="addWatchlist"),
    path("removeWatchlist/<int:auction_id>", views.removeWatchlist, name="removeWatchlist"),
    path("comment/<int:auction_id>", views.comment, name="comment"),
    path("bid/<int:auction_id>", views.bid, name="bid"),
    path("category/<str:category>", views.category, name="category"),
    path("categories", views.categories, name="categories"),
    path("close/<int:auction_id>", views.close, name="close")
]
