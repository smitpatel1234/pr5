# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("twitter/login/", views.twitter_login, name="twitter_login"),
    path("twitter/callback/", views.twitter_callback, name="twitter_callback"),
        path("twitter/<str:username>/", views.twitter_profile_api, name="twitter_profile"),

]
