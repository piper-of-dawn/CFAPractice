"""
URL configuration for mcq project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from quiz.views import (
    home,
    play,
    mcq,
    reset,
    api_mistake,
    api_mistakes_count,
    api_mistakes_dump,
    mistakes,
    mistakes_grouped,
    master,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    # Allow subfolders inside data/ via <path:fname>
    path('play/<path:fname>/', play, name='play'),
    path('master/', master, name='master'),
    path('mistakes/', mistakes, name='mistakes'),
    path('mistakes/topics/', mistakes_grouped, name='mistakes_grouped'),
    path('api/mistake/', api_mistake, name='api_mistake'),
    path('api/mistakes_count/', api_mistakes_count, name='api_mistakes_count'),
    path('api/mistakes_dump/', api_mistakes_dump, name='api_mistakes_dump'),
    path('legacy/', mcq, name='mcq'),
    path('reset/', reset, name='reset'),
]
