from django.urls import path
# from .views import home
from . import views

urlpatterns = [
    path('signup',views.signup,name='signup'),
    path('login',views.Login,name='login'),
    path('dashboard',views.dashboard,name='dashboard'),
    path('logout',views.logout,name='logout'),
    path('forgotpassword',views.forgotpassword,name='forgotpassword'),
    path('payment',views.payment,name='payment'),
    path('payment/success',views.payment_success,name='payment_success'),
    path('feedback',views.feedback_view,name='feedback'),
]
