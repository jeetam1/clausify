# summarizer/urls.py
from django.urls import path
from ..clausify.summarized import views

urlpatterns = [
    path('', views.index, name='index'),
    path('summarize/', views.summarize, name='summarize'),
]