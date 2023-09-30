"""
URL configuration for RoutingApp project.

The `urlpatterns` list routes URLs to views. For more information, please see:
https://docs.djangoproject.com/en/4.2/topics/http/urls/

Examples:
Function views:
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')

Class-based views:
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')

Including another URLconf:
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# Django
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

# local Django
from myApplication import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', auth_views.LogoutView.as_view(next_page='welcome'),
         name='logout'),
    path('home/', views.home, name='home'),
    path('reroute/', views.build_routes, name='build_routes'),
    path('admin/', admin.site.urls),
]
