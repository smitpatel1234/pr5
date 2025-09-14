from  django.urls import path
from . import views
urlpatterns=[
    path('smit/',views.smit,name='smit')
]
