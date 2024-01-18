"""dispatch URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path, include
from app import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name='index'),
    path("report/", views.report, name='report'),
    path("report/<str:id>", views.report, name='report'),
    path("map/", views.map_view, name='map'),
    path("c/<str:id>", views.case, name='c'),
    path("accounts/",include("django.contrib.auth.urls")),
    path("register/", views.register, name='register'),
    path("log/", views.log, name='log'),
]
