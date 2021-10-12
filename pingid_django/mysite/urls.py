"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from django.contrib import admin
from mysite import views

app_name = 'mysite'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pingid.urls')), #https://stackoverflow.com/questions/58357047/how-to-properly-redirect-from-one-app-to-another-app-in-django
    path('', views.index, name='index'), #app entry point
    path('callback/', views.callback, name='callback'), #listener for redirect uri
    path('hello/', views.hello, name='hello') #fake app landing page 
]
