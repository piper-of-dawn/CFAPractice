from django.contrib import admin
from django.urls import path
from quiz.views import mcq, reset, flashcards_index, flashcards_render

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", mcq, name="mcq"),
    path("reset/", reset, name="reset"),
    path("flashcards/", flashcards_index, name="flashcards_index"),
    path("flashcards/<str:name>/", flashcards_render, name="flashcards_render"),
]
