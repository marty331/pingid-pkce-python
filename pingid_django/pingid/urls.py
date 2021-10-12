from django.urls import path

from pingid import views

app_name = 'pingid'
urlpatterns = [
    path('login/', views.login, name='login'),
    path('pingauthrequired/', views.pingauthrequired, name='pingauthrequired' ),
    path('obtaintoken/', views.obtaintoken, name='obtaintoken' ),
    path('usesql/', views.usesql, name='usesql' )
]