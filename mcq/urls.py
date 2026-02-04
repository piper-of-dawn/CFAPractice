from django.contrib import admin
from django.urls import path
from quiz.views import mcq, reset

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", mcq, name="mcq"),
    path("reset/", reset, name="reset"),
]
