from django.urls import path
# from .views import home
from . import views

urlpatterns = [
    path('signup',views.signup,name='signup'),
    path('login',views.Login,name='login'),
    path('dashboard',views.dashboard,name='dashboard'),
    path('logout',views.logout,name='logout'),
    path('forgotpassword',views.forgotpassword,name='forgotpassword'),
]
